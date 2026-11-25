import { getServerSession } from 'next-auth';
import { NextResponse } from 'next/server';
import { authOptions } from '../../auth/[...nextauth]/route';
import { issueDatasetTicket } from '../../../../../lib/datasets';

export async function POST() {
  const session = await getServerSession(authOptions);
  if (!session?.userId) {
    return NextResponse.json({ error: 'Sign in before uploading a file.' }, { status: 401 });
  }
  const token = await issueDatasetTicket('upload_tickets', { user_id: session.userId });
  return NextResponse.json({ token }, { headers: { 'Cache-Control': 'no-store' } });
}
