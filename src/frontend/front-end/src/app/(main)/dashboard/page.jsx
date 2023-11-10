import TextBox from "../../../components/TextBox"
import { HomeIcon } from '@heroicons/react/24/solid'

export default function page() {
    return (
    <div className="grid grid-cols-3 w-screen min-h-screen bg-[#F6F6F6]">
        {/* <!-- This is the first item at the top-left corner spanning 2 columns --> /} */}
        <div className="bg-blue-500 row-span-1 col-span-2 m-3">
            {/* put the home icon and drop down menu here */}
            <div>
                {/* Home icon */}
                <button>
                    <HomeIcon className="w-10 h-10"/>
                </button>
            </div>
        </div>
        <div className="bg-red-500 row-span-2 col-span-1">2</div>

        {/* <!-- TextBox should span the entire height minus the first row and span all columns --> /} */}
        <TextBox className="col-span-2 row-span-full pl-3 pr-3"/>

        {/* <!-- These two divs are placed on the right side, each occupying a single column and multiple rows --> */}
        <div className="bg-green-500 row-span-2 col-span-1">3</div>
    </div>
    )
}
  