import React from 'react';
import { authOptions } from "../../api/auth/[...nextauth]/route";
import { getServerSession } from "next-auth";
import { redirect } from "next/navigation";
import UserMenu from '../../../components/UserMenu';

export default async function Page() {
  const session = await getServerSession(authOptions);    
  if (!session) {
      redirect('/login');
  }

  return (
    <section className='min-h-screen flex flex-col justify-between bg-bgGrey text-black'>
    {/* Search bar and User Menu at the top */}
    <div className="flex w-full justify-center items-center relative p-12">
      <div className="flex-grow flex justify-center">
        <input
          type="text"
          placeholder="Search for a dataset..."
          className="bg-gray-200 text-gray-800 p-2 rounded-md"
        />
      </div>
      <div className="relative">
        <UserMenu/>
      </div>
    </div>
  </section>
  );
}
