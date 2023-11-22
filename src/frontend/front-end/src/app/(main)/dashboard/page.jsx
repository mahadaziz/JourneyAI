import { HomeIcon } from '@heroicons/react/24/solid';
import { authOptions } from "../../api/auth/[...nextauth]/route";
import { getServerSession } from "next-auth";
import { redirect } from "next/navigation";
import TextBox from "../../../components/TextBox"
import ThemeSwitcher from "../../../components/ThemeSwitcher"
import SideNav from "../../../components/SideNav"
import OptionsMenu from "../../../components/OptionsMenu"
import HypothesisBox from "../../../components/HypothesisBox";
import InsightsBox from "../../../components/InsightsBox";
import '../../../app/globals.css'

export default async function page() {
    const session = await getServerSession(authOptions);    
    if (!session) {
        redirect('/login');
    }

    return (
    <div className="grid grid-cols-3 w-screen min-h-screen bg-bgGrey delayAnimation transition-colors duration-100 ease-in-out dark:bg-neutral-900">
        {/* <!-- This is the first item at the top-left corner spanning 2 columns --> /} */}
        <div className="row-span-1 col-span-2 m-3">
            {/* put the home icon and drop down menu here */}
            <div className="flex flex-row justify-between items-center">
                <div className="flex flex-row justify-content items-center align-center border border-gray-700 ml-2 pl-2 pr-2 rounded-2xl bg-white dark:bg-neutral-900">
                    <a href="/homepage">
                        <button className="p-2 rounded-lg hover:text-bgLight hover:bg-gray-300 dark:hover:bg-gray-700">
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
        <div className="row-span-2 col-span-1">
            <HypothesisBox/>
        </div>

        {/* <!-- TextBox should span the entire height minus the first row and span all columns --> /} */}
        <TextBox className="col-span-2 row-span-full pl-3 pr-3 "/>

        {/* <!-- These two divs are placed on the right side, each occupying a single column and multiple rows --> */}
        <div className="row-span-2 col-span-1">
            <InsightsBox/>
        </div>
    </div>
    )
}