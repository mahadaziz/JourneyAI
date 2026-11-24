import { connectMongoDB } from './mongodb';

export async function findDraft(dataset, userId) {
  const { connection } = await connectMongoDB();
  const documents = connection.collection('documents');
  const projection = {
    title: 1, content: 1, text: 1, revision: 1,
  };
  const byDataset = { user_id: userId, dataset_id: dataset._id.toString() };
  const linked = await documents.findOne(byDataset, { projection });
  if (linked) return linked;

  // Early uploads linked the two collections by title. Only adopt an unambiguous match.
  const byTitle = { user_id: userId, title: dataset.title };
  const unlinked = { ...byTitle, dataset_id: { $exists: false } };
  const legacy = await documents.find(unlinked, { projection }).limit(2).toArray();
  if (legacy.length !== 1) return null;
  const matches = await connection.collection('datasets').countDocuments(byTitle, { limit: 2 });
  return matches === 1 ? legacy[0] : null;
}

export function editorDraft(stored, datasetTitle) {
  const paragraphs = (stored?.text || '').split(/\r?\n/).map((text) => (
    text ? { type: 'paragraph', content: [{ type: 'text', text }] } : { type: 'paragraph' }
  ));
  return {
    title: stored?.title ?? datasetTitle,
    content: stored?.content ?? { type: 'doc', content: paragraphs },
    revision: stored?.revision ?? 0,
  };
}
