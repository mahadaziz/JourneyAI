export default function Page() {
  return (
    <section className='min-h-screen flex flex-col justify-between bg-bgGrey text-black'>
      
      {/* Search bar and User Menu at the top */}
      <div className="flex items-center p-12">
        <div className="flex justify-center">
          <input
            type="text"
            placeholder="Search for a dataset..."
            className="bg-gray-200 text-gray-800 p-2 rounded-md"
          />
        </div>

        
      </div>

      {/* Dataset cards in the middle */}
      <div className="flex justify-center items-center grid grid-cols-4 bg-bgGrey text-center max-w-screen-md mx-auto">
        {/* First Row */}
        <div className="h-48 w-36 bg-white rounded-lg shadow-lg shadow-bottom py-4 mx-5 mb-6">
          <p className="text-lg">Upload Dataset</p>
        </div>

        <div className="h-48 w-36 bg-white rounded-lg shadow-lg shadow-bottom py-4 mx-5 mb-6">
          <p className="text-lg">Fuel Consumption</p>
        </div>
      </div>

      {/* Copyright message at the bottom */}
      <div className="relative bottom-0 left-0 right-0 p-4 text-center bg-bgGrey">
        2023 Journey AI, All rights reserved
      </div>
    </section>
  );
}