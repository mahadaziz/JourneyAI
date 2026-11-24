import { Types } from 'mongoose';
import { connectMongoDB } from './mongodb';

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
