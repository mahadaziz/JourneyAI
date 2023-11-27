'use client'

const HypothesisButton = ({ header }) => {
    return (
        <div className="px-4 py-2">
            <button type="button" className="flex flex-col items-center w-full bg-white border border-gray-200 rounded-lg shadow md:flex-row md:max-w-xl hover:bg-gray-100 dark:border-gray-700 dark:bg-gray-800 dark:hover:bg-gray-700">
            <h5 className="text-xl font-normal tracking-tight p-4 text-gray-900 dark:text-white">
                {header}
            </h5>
            <p className="mb-3 font-normal text-gray-700 dark:text-gray-400"></p>
            </button>
        </div>
    )
}

const HypothesisBox = () => {
    const hypothesisHeaders = [
        'Hypothesis Generation Header 1',
        'Hypothesis Generation Header 2',
        'Hypothesis Generation Header 3'
    ];

    return (
        <div className="px-2 w-full">
            <div className="flex justify-between items-center bg-neutral-900 border border-gray-200 rounded-lg shadow md:flex-row md:max-w-xl dark:border-gray-700 dark:bg-gray-800 dark:hover:bg-gray-700">
                <div className="flex flex-col justify-between p-4 leading-normal">
                    <h5 className="mb-2 text-2xl font-bold tracking-tight text-white dark:text-white">
                        Hypotheses
                    </h5>
                </div>
                <button type="button" className="text-white bg-gray-600 hover:bg-gray-400 focus:outline-none focus:ring-4 focus:ring-gray-300 font-medium rounded-full text-sm px-5 py-2.5 text-center inline-flex items-center me-2 dark:text-gray-800 dark:bg-white dark:hover:bg-gray-300 dark:focus:ring-gray-700 dark:border-gray-700">
                    Refresh
                </button>
            </div>
            {hypothesisHeaders.map((header, index) => (
                <HypothesisButton key={index} header={header} />
            ))}
        </div>
    )
}

export default HypothesisBox
