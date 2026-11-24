import { getServerSession } from 'next-auth';
import { NextResponse } from 'next/server';
import { authOptions } from '../../../auth/[...nextauth]/route';
import { findUserDataset } from '../../../../../../lib/datasets';

export async function POST(request, { params }) {
  const session = await getServerSession(authOptions);
  if (!session?.userId) {
    return NextResponse.json({ error: 'Sign in to view this dataset.' }, { status: 401 });
  }
  const dataset = await findUserDataset(session.userId, params.id, { data: 1, column_names: 1 });
  if (!dataset) {
    return NextResponse.json({ error: 'Dataset not found.' }, { status: 404 });
  }
  const body = await request.json();
  if (!dataset.column_names.includes(body.column_name)) {
    return NextResponse.json({ error: 'Choose a column from this dataset.' }, { status: 400 });
  }
  const apiUrl = process.env.FLASK_INTERNAL_URL || process.env.NEXT_PUBLIC_LOCAL_URL;
  try {
    const response = await fetch(`${apiUrl}/get_insights`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      cache: 'no-store',
      body: JSON.stringify({
        rows: dataset.data,
        column_name: body.column_name,
        prev_insights: body.prev_insights,
        insight_count: body.insight_count,
      }),
    });
    return NextResponse.json(await response.json(), { status: response.status });
  } catch {
    return NextResponse.json({ error: 'The analysis service is unavailable.' }, { status: 502 });
  }
}
