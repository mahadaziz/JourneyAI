import TextBox from "../../../components/TextBox";

import '../../globals.css';

export default function page() {
    return (
    <div className="grid grid-rows-4 grid-cols-3 grid-flow-col gap-4 w-screen h-screen bg-[#F6F6F6]">
        {/* <!-- This is the first item at the top-left corner spanning 2 columns --> */}
        <div className="bg-blue-500 row-span-1 col-span-2">1</div>

        {/* <!-- TextBox should span the entire height minus the first row and span all columns --> */}
        <TextBox/>

        {/* <!-- These two divs are placed on the right side, each occupying a single column and multiple rows --> */}
        <div className="bg-red-500 row-span-2 col-span-1">2</div>
        <div className="bg-green-500 row-span-2 col-span-1">3</div>
    </div>
    )
}

{/* <div className="grid grid-rows-4 grid-cols-3 grid-flow-col gap-4 w-screen h-screen bg-[#F6F6F6]">
    <div className="bg-blue-500 row-span-1 col-span-3">1</div>

    <TextBox className="row-span-4 col-span-2"/>

    <div className="bg-red-500 row-span-2 col-span-2">2</div>
    <div className="bg-green-500 row-span-1 col-span-2">3</div>
</div> */}
  