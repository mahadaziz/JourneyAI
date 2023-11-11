import TextBox from "../../../components/TextBox"
import OptionsMenu from "../../../components/OptionsMenu"
import { HomeIcon } from '@heroicons/react/24/solid'
import ThemeSwitcher from "../../../components/ThemeSwitcher"
import '../../../app/globals.css'

export default function page() {
    return (
    <div className="grid grid-cols-3 w-screen min-h-screen bg-[#F6F6F6] transition-colors duration-200 ease-in dark:bg-black">
        {/* <!-- This is the first item at the top-left corner spanning 2 columns --> /} */}
        <div className=" row-span-1 col-span-2 m-3">
            {/* put the home icon and drop down menu here */}
            <div className="flex flex-row justify-between items-center">
                <a href="/homepage">
                    <button>
                        <HomeIcon className="w-10 h-10 delayAnimation"/>
                    </button>
                </a>
                {/* DropDown Menu */}
                <div className="flex flex-grow justify-center delayAnimation z-10">
                    <OptionsMenu/>
                </div>

                <div>
                    <ThemeSwitcher/>
                </div>
            </div>
        </div>
        <div className="bg-red-500 row-span-2 col-span-1">2</div>

        {/* <!-- TextBox should span the entire height minus the first row and span all columns --> /} */}
        <TextBox className="col-span-2 row-span-3 pl-3 pr-3"/>

        {/* <!-- These two divs are placed on the right side, each occupying a single column and multiple rows --> */}
        <div className="bg-green-500 row-span-2 col-span-1">3</div>
    </div>
    )
}
  