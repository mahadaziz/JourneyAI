import React from 'react';
import { getServerSession } from 'next-auth';
import { redirect } from 'next/navigation';
import { authOptions } from '../../api/auth/[...nextauth]/route';
import HomeSideNav from '../../../components/HomeSideNav';
import { connectMongoDB } from '../../../../lib/mongodb';
import UserCard from '../../../components/UserCard';
import OpenHomeSideNav from '../../../components/OpenHomeSideNav';
import ThemeSwitcher from '../../../components/ThemeSwitcher';
import '../../globals.css';

export default async function Page() {
  const session = await getServerSession(authOptions);
  if (!session?.userId) {
    redirect('/login');
  }
  const { connection } = await connectMongoDB();
  const owner = { user_id: session.userId };
  const savedDrafts = { ...owner, revision: { $gt: 0 } };
  const titlesOnly = { projection: { dataset_id: 1, title: 1 } };
  const [datasets, drafts] = await Promise.all([
    connection.collection('datasets').find(owner, { projection: { title: 1, column_names: 1 } })
      .sort({ _id: -1 }).toArray(),
    connection.collection('documents').find(savedDrafts, titlesOnly).toArray(),
  ]);
  const titles = new Map(drafts.map((draft) => [draft.dataset_id, draft.title]));

  return (
    <div className="h-screen flex bg-bgGrey text-black">
      <div className="hidden min-w-[300px] lg:block">
        <HomeSideNav session={session} />
      </div>

      <div className="block lg:hidden">
        <OpenHomeSideNav session={session} />
      </div>

      <section className="h-screen grid grid-rows-[auto_1fr] grid-cols-3 lg:grid-cols-4 xl:grid-cols-6 p-3
       bg-bgGrey text-black dark:bg-black transition-colors duration-500 ease-in-out"
      >
        <div className="col-span-3 sm:col-span-5 flex flex-row justify-between items-center pt-5 pl-12 delayAnimationSearch">
          {/* <SearchBar /> */}
          <div className="absolute right-12 pt-12 pr-12">
            <ThemeSwitcher />
          </div>
        </div>
        <div className="col-span-5 md:col-span-4 lg:col-span-4 xl:col-span-5 p-12 overflow-auto homepage delayAnimation">
          <div className="flex flex-col md:grid md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
            {datasets.map((dataset) => (
              <UserCard
                key={dataset._id.toString()}
                datasetId={dataset._id.toString()}
                title={titles.get(dataset._id.toString()) ?? dataset.title}
                description={dataset.column_names.join(', ')}
              />
            ))}
            <UserCard title="Upload Dataset" description="" isUploadCard />
          </div>
        </div>
      </section>
    </div>
  );
}
