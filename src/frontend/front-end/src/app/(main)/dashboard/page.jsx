import TextBox from "../../../components/TextBox"
import OptionsMenu from "../../../components/OptionsMenu"
import { HomeIcon } from '@heroicons/react/24/solid';
import ThemeSwitcher from "../../../components/ThemeSwitcher"
import SideNav from "../../../components/SideNav"
import '../../../app/globals.css'

export default function page() {
    return (
    <div className="grid grid-cols-3 w-screen min-h-screen bg-bgGrey delayAnimation transition-colors duration-500 ease-in dark:bg-neutral-900">
        {/* <!-- This is the first item at the top-left corner spanning 2 columns --> /} */}
        <div className="row-span-1 col-span-2 m-3">
            {/* put the home icon and drop down menu here */}
            <div className="flex flex-row justify-between items-center">
                <div className="flex flex-row justify-content items-center align-center border border-gray-700 ml-2 pl-2 pr-2 rounded-2xl bg-white dark:bg-neutral-900">
                    <a href="/homepage">
                        <button className="p-2 hover:text-bgLight hover:bg-gray-300 dark:hover:bg-gray-700 rounded-lg">
                            <HomeIcon className="w-6 h-6 "/>
                        </button>
                    </a>
                    <SideNav/>
                </div>
                {/* DropDown Menu */}
                <div className="flex flex-grow justify-center z-10">
                    <OptionsMenu/>
                </div>

                <div className="bg-white dark:bg-neutral-900 rounded-2xl">
                    <ThemeSwitcher/>
                </div>
            </div>
        </div>
        <div className="row-span-2 col-span-1">2</div>

        {/* <!-- TextBox should span the entire height minus the first row and span all columns --> /} */}
        <TextBox className="col-span-2 row-span-full pl-3 pr-3 "/>

        {/* <!-- These two divs are placed on the right side, each occupying a single column and multiple rows --> */}
        <div className="row-span-2 col-span-1">3</div>
    </div>
    )
}