import React from 'react';
import { getServerSession } from 'next-auth';
import { redirect } from 'next/navigation';
import { authOptions } from '../../api/auth/[...nextauth]/route';
import HomeSideNav from '../../../components/HomeSideNav';
import SearchBar from '../../../components/SearchBar';
import UserCard from '../../../components/UserCard';
import OpenHomeSideNav from '../../../components/OpenHomeSideNav';
import ThemeSwitcher from '../../../components/ThemeSwitcher';
import '../../globals.css';

export default async function Page() {
  const session = await getServerSession(authOptions);
  if (!session) {
    redirect('/login');
  }
  // Array simulating data from the database
  const cardsData = [
    { title: 'The Consumption of Cars during the years', description: 'Here are the biggest enterprise technology acquisitions of 2021 so far, in reverse chronological order. Here are the biggest enterprise technology acquisitions of 2021 so far, in reverse chronological order. Here are the biggest enterprise technology acquisitions of 2021 so far, in reverse chronological order.', isUploadCard: false },
  ];

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
            {cardsData.map((card) => (
              <div key={card.title}>
                <UserCard
                  title={card.title}
                  description={card.description}
                  isUploadCard={card.isUploadCard}
                  sessionId={card.sessionId}
                  userId={card.userId}
                />
              </div>
            ))}
            <UserCard title="Upload Dataset" description="" isUploadCard sessionId={session.sessionId} userId={session.userId} />
          </div>
        </div>
      </section>
    </div>
  );
}
