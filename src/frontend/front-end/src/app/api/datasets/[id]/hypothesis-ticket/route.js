import { getServerSession } from 'next-auth';
import { NextResponse } from 'next/server';
import { authOptions } from '../../../auth/[...nextauth]/route';
import { findUserDataset, issueDatasetTicket } from '../../../../../../lib/datasets';

export async function POST(request, { params }) {
  const session = await getServerSession(authOptions);
  if (!session?.userId) {
    return NextResponse.json({ error: 'Sign in to generate hypotheses.' }, { status: 401 });
  }
  const dataset = await findUserDataset(session.userId, params.id, { title: 1, column_names: 1 });
  if (!dataset) return NextResponse.json({ error: 'Dataset not found.' }, { status: 404 });
  const body = await request.json().catch(() => null);
  if (!dataset.column_names.includes(body?.column_name)) {
    return NextResponse.json({ error: 'Choose a column from this dataset.' }, { status: 400 });
  }
  const token = await issueDatasetTicket('hypothesis_tickets', {
    user_id: session.userId,
    dataset_id: params.id,
    dataset_name: dataset.title,
    column_name: body.column_name,
  });
  return NextResponse.json({ token }, { headers: { 'Cache-Control': 'no-store' } });
}
