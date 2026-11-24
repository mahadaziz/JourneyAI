import { randomBytes } from 'crypto';
import { getServerSession } from 'next-auth';
import { NextResponse } from 'next/server';
import { authOptions } from '../../auth/[...nextauth]/route';
import { connectMongoDB } from '../../../../../lib/mongodb';

export async function POST() {
  const session = await getServerSession(authOptions);
  if (!session?.userId) {
    return NextResponse.json({ error: 'Sign in before uploading a file.' }, { status: 401 });
  }
  const { connection } = await connectMongoDB();
  const tickets = connection.collection('upload_tickets');
  await tickets.createIndex({ expires_at: 1 }, { expireAfterSeconds: 0 });
  const token = randomBytes(32).toString('hex');
  await tickets.insertOne({
    _id: token,
    user_id: session.userId,
    expires_at: new Date(Date.now() + 10 * 60 * 1000),
  });
  return NextResponse.json({ token }, { headers: { 'Cache-Control': 'no-store' } });
}
