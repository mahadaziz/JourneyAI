import React from 'react';
import { getServerSession } from 'next-auth';
import { notFound, redirect } from 'next/navigation';
import { authOptions } from '../../api/auth/[...nextauth]/route';
import { editorDraft, findDraft } from '../../../../lib/drafts';
import { findUserDataset } from '../../../../lib/datasets';
import { EditorDataProvider } from '../../../context/EditorDataContext';
import { SelectedColumnProvider } from '../../../context/SelectedColumnContext';
import { HypothesisDataProvider } from '../../../context/HypothesisDataContext';
import { InsightsDataProvider } from '../../../context/InsightsDataContext';
import TextBox from '../../../components/TextBox';
import HypothesisBox from '../../../components/HypothesisBox';
import InsightsBox from '../../../components/InsightsBox';
import NavBar from '../../../components/NavBar';
import '../../globals.css';

export default async function Dashboard({ searchParams }) {
  const session = await getServerSession(authOptions);
  if (!session?.userId) {
    redirect('/login');
  }
  const projection = { title: 1, column_names: 1 };
  const dataset = await findUserDataset(session.userId, searchParams.dataset, projection);
  if (!dataset) {
    if (searchParams.dataset !== undefined) notFound();
    redirect('/homepage');
  }
  const datasetId = dataset._id.toString();
  const metadata = { title: dataset.title, columns: dataset.column_names };
  if (searchParams.dataset === undefined) redirect(`/dashboard?dataset=${datasetId}`);
  const stored = await findDraft(dataset, session.userId);
  const draft = editorDraft(stored, dataset.title);
  return (
    <EditorDataProvider
      key={datasetId}
      datasetId={datasetId}
      initialTitle={draft.title}
      revision={draft.revision}
    >
      <SelectedColumnProvider>
        <InsightsDataProvider>
          <HypothesisDataProvider>
            <div className="grid grid-rows-[auto_1fr] grid-cols-6 w-screen h-screen bg-bgGrey delayAnimation transition-colors duration-500 ease-in-out dark:bg-neutral-900">
              <div className="col-span-5 md:col-span-6 pb-2">
                <div className="flex flex-row justify-between items-center w-full">
                  <NavBar
                    datasetId={datasetId}
                    dataset={metadata}
                    userId={session.userId}
                    sessionId={session.sessionId}
                  />
                </div>
              </div>

              <div className="flex flex-col col-span-5 md:col-span-3 pt-4 h-full overflow-y-auto">
                <TextBox datasetId={datasetId} draft={draft} />
              </div>

              <div className="hidden md:flex md:flex-col md:col-span-3 pt-4">
                <div className="w-full overflow-y-auto">
                  <HypothesisBox
                    datasetId={datasetId}
                    sessionId={session.sessionId}
                  />
                </div>
                <div className="w-full py-8 overflow-y-auto">
                  <InsightsBox datasetId={datasetId} />
                </div>
              </div>
            </div>
          </HypothesisDataProvider>
        </InsightsDataProvider>
      </SelectedColumnProvider>
    </EditorDataProvider>
  );
}
