import TextBox from "../../../components/TextBox";

import '../../globals.css';

export default function page() {
    return (
    <div className="grid grid-rows-4 grid-cols-3 grid-flow-col w-screen min-h-screen bg-[#F6F6F6]">
        {/* <!-- This is the first item at the top-left corner spanning 2 columns --> */}
        <div className="bg-blue-500 row-span-1 col-span-2 h-[100px]">1</div>

        {/* <!-- TextBox should span the entire height minus the first row and span all columns --> */}
        <TextBox/>

        {/* <!-- These two divs are placed on the right side, each occupying a single column and multiple rows --> */}
        <div className="bg-red-500 row-span-2 col-span-1">2</div>
        <div className="bg-green-500 row-span-2 col-span-1">3</div>
    </div>
    )
}
  