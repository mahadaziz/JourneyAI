import { Types } from 'mongoose';
import { randomBytes } from 'crypto';
import { connectMongoDB } from './mongodb';

export async function issueDatasetTicket(collectionName, scope) {
  const { connection } = await connectMongoDB();
  const tickets = connection.collection(collectionName);
  await tickets.createIndex({ expires_at: 1 }, { expireAfterSeconds: 0 });
  const token = randomBytes(32).toString('hex');
  await tickets.insertOne({
    _id: token, ...scope, expires_at: new Date(Date.now() + 10 * 60 * 1000),
  });
  return token;
}

export async function findUserDataset(userId, datasetId, projection) {
  if (!userId) return null;
  const query = { user_id: userId };
  if (datasetId !== undefined) {
    if (typeof datasetId !== 'string' || !/^[a-f\d]{24}$/i.test(datasetId)) return null;
    query._id = new Types.ObjectId(datasetId);
  }
  const { connection } = await connectMongoDB();
  return connection.collection('datasets').findOne(query, {
    projection,
    sort: { _id: -1 },
  });
}
