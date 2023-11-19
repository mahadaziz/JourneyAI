'use client'

const HypothesisBox = () => {
    return (
        <div className="p-4 w-full">
            <div class="flex justify-between items-center bg-white border border-gray-200 rounded-lg shadow md:flex-row md:max-w-xl hover:bg-gray-100 dark:border-gray-700 dark:bg-gray-800 dark:hover:bg-gray-700">
                <div class="flex flex-col justify-between p-4 leading-normal">
                    <h5 class="mb-2 text-2xl font-bold tracking-tight text-gray-900 dark:text-white">
                        Hypotheses
                    </h5>
                </div>
                <button type="button" class="text-white bg-gray-800 hover:bg-gray-900 focus:outline-none focus:ring-4 focus:ring-gray-300 font-medium rounded-full text-sm px-5 py-2.5 text-center inline-flex items-center me-2 dark:text-gray-800 dark:bg-white dark:hover:bg-gray-300 dark:focus:ring-gray-700 dark:border-gray-700">
                    Refresh
                </button>
            </div>
            <button type="button" className="flex flex-col items-center w-full bg-white border border-gray-200 rounded-lg shadow md:flex-row md:max-w-xl p-4 hover:bg-gray-100 dark:border-gray-700 dark:bg-gray-800 dark:hover:bg-gray-700">
                    <h5 className="mb-2 text-2xl font-normal tracking-tight text-gray-900 dark:text-white">
                        Hypothesis Generation Header 1
                    </h5>
                    <p className="mb-3 font-normal text-gray-700 dark:text-gray-400"></p>
            </button>
            <button type="button" className="flex flex-col items-center w-full bg-white border border-gray-200 rounded-lg shadow md:flex-row md:max-w-xl p-4 hover:bg-gray-100 dark:border-gray-700 dark:bg-gray-800 dark:hover:bg-gray-700">
                    <h5 className="mb-2 text-2xl font-normal tracking-tight text-gray-900 dark:text-white">
                        Hypothesis Generation Header 2
                    </h5>
                    <p className="mb-3 font-normal text-gray-700 dark:text-gray-400"></p>
            </button>
            <button type="button" className="flex flex-col items-center w-full bg-white border border-gray-200 rounded-lg shadow md:flex-row md:max-w-xl p-4 hover:bg-gray-100 dark:border-gray-700 dark:bg-gray-800 dark:hover:bg-gray-700">
                    <h5 className="mb-2 text-2xl font-normal tracking-tight text-gray-900 dark:text-white">
                        Hypothesis Generation Header 3
                    </h5>
                    <p className="mb-3 font-normal text-gray-700 dark:text-gray-400"></p>
            </button>
        </div>
    )
}

export default HypothesisBox
