import { getSchema } from '@tiptap/core';
import StarterKit from '@tiptap/starter-kit';
import Underline from '@tiptap/extension-underline';
import { getServerSession } from 'next-auth';
import { NextResponse } from 'next/server';
import { authOptions } from '../../../auth/[...nextauth]/route';
import { findUserDataset } from '../../../../../../lib/datasets';
import { findDraft } from '../../../../../../lib/drafts';
import { connectMongoDB } from '../../../../../../lib/mongodb';

const schema = getSchema([StarterKit, Underline]);

export async function PUT(request, { params }) {
  const session = await getServerSession(authOptions);
  if (!session?.userId) {
    return NextResponse.json({ error: 'Sign in to save your draft.' }, { status: 401 });
  }
  const dataset = await findUserDataset(session.userId, params.id, { title: 1 });
  if (!dataset) return NextResponse.json({ error: 'Dataset not found.' }, { status: 404 });

  let body;
  let document;
  try {
    body = await request.json();
    document = schema.nodeFromJSON(body.content);
    if (document.type !== schema.topNodeType) throw new Error();
    document.check();
  } catch {
    return NextResponse.json({ error: 'Invalid draft content.' }, { status: 400 });
  }
  if (typeof body.title !== 'string' || !body.title.trim()
      || !Number.isSafeInteger(body.revision) || body.revision < 0) {
    return NextResponse.json(
      { error: 'Enter a title and a valid draft revision.' },
      { status: 400 },
    );
  }

  const existing = await findDraft(dataset, session.userId);
  const { connection } = await connectMongoDB();
  const documents = connection.collection('documents');
  const target = { _id: existing?._id ?? params.id, user_id: session.userId };
  const content = document.toJSON();
  // Old records acquire their dataset ID and first revision in the same update.
  const revision = body.revision === 0 ? { $in: [0, null] } : body.revision;
  try {
    const saved = await documents.updateOne({ ...target, revision }, {
      $set: {
        dataset_id: params.id,
        title: body.title,
        content,
        text: document.textBetween(0, document.content.size, '\n'),
        last_update_time: new Date(),
        revision: body.revision + 1,
      },
    }, { upsert: !existing && body.revision === 0 });
    if (saved.modifiedCount || saved.upsertedCount) {
      return NextResponse.json({ revision: body.revision + 1 });
    }
  } catch (error) {
    if (error.code !== 11000) throw error;
  }
  // A retry after a lost response can acknowledge the already-persisted edit.
  const projection = { title: 1, content: 1, revision: 1 };
  const latest = await documents.findOne(target, { projection });
  if (latest?.title === body.title && JSON.stringify(latest.content) === JSON.stringify(content)) {
    return NextResponse.json({ revision: latest.revision });
  }
  return NextResponse.json(
    { error: 'A newer draft was saved in another tab. Copy your edits before reloading.' },
    { status: 409 },
  );
}
