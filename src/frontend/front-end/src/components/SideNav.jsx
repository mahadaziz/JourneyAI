'use client';
import { useState, useEffect, useRef } from "react";
import { signOut } from "next-auth/react";
import { useRouter } from 'next/navigation';

const SideNav = () => {
    const [isOpen, setIsOpen] = useState(false);
    const sidebarRef = useRef(); // Create a ref for the sidebar
    const router = useRouter();
    // Function to toggle the dropdown state
    const toggleDropdown = () => setIsOpen(!isOpen);

    useEffect(() => {
        // Function to close the sidebar if a click is detected outside of it
        const handleClickOutside = (event) => {
            if (isOpen && sidebarRef.current && !sidebarRef.current.contains(event.target)) {
                setIsOpen(false); // Close the sidebar
            }
        };

        // Add event listener when the component is mounted
        document.addEventListener('mousedown', handleClickOutside);

        // Remove event listener when the component is unmounted
        return () => {
            document.removeEventListener('mousedown', handleClickOutside);
        };
    }, [isOpen]); // Only re-run if isOpen changes

    const handleSignOut = async () => {
        console.log("SignOut");
        await signOut({ redirect: true, callbackUrl: '/login' });
        await fetch("http://127.0.0.1:5000/signout");
        // try {
        //     // Attempt to sign out using NextAuth
        //     const nextResp = await signOut();
    
        //     // Make your additional signout request
        //     const response = await fetch("http://127.0.0.1:5000/signout");
    
        //     // Check if the response was successful
        //     if (nextResp.ok && response.ok) {
        //         // Redirect to a specific page after successful sign out
        //         router.push('/login');
        //     } else {
        //         // Handle failed sign out attempt (fetch request failed)
        //         console.error('Failed to sign out from the external service');
        //     }
        // } catch (error) {
        //     // Handle any errors that occurred during sign out
        //     console.error('Error during sign out:', error);
        // }
    }

    return (
        <div>
            <button onClick={toggleDropdown} data-drawer-target="sidebar-multi-level-sidebar" data-drawer-toggle="sidebar-multi-level-sidebar" aria-controls="sidebar-multi-level-sidebar" type="button" 
                className="inline-flex items-center p-2 ms-1 text-sm hover:text-bgLight hover:bg-gray-300 rounded-lg focus:outline-none dark:hover:bg-gray-700">
                
                <span className="sr-only">Open sidebar</span>
                <svg className="w-6 h-6" aria-hidden="true" fill="currentColor" viewBox="0 0 20 20" xmlns="http://www.w3.org/2000/svg">
                <path clipRule="evenodd" fillRule="evenodd" d="M2 4.75A.75.75 0 012.75 4h14.5a.75.75 0 010 1.5H2.75A.75.75 0 012 4.75zm0 10.5a.75.75 0 01.75-.75h7.5a.75.75 0 010 1.5h-7.5a.75.75 0 01-.75-.75zM2 10a.75.75 0 01.75-.75h14.5a.75.75 0 010 1.5H2.75A.75.75 0 012 10z"></path>
                </svg>
            </button>

            <aside ref={sidebarRef} id="sidebar-multi-level-sidebar" className={`${isOpen ? 'translate-x-0' : '-translate-x-full'} absolute top-0 left-0 z-40 w-64 h-screen transition-transform -translate-x-full sm:translate-x-0" aria-label="Sidebar`}>
            <div className="absolute h-full px-3 py-4 overflow-y-auto bg-gray-50 dark:bg-gray-800">
                <ul className="space-y-2 font-medium">
                    <li>
                        <a href="#" className="flex items-center p-2 text-gray-900 rounded-lg dark:text-white hover:bg-gray-100 dark:hover:bg-gray-700 group">
                        <span className="ms-3">Home</span>
                        </a>
                    </li>
                    <li>
                        <button type="button" className="flex items-center w-full p-2 text-base text-gray-900 transition duration-75 rounded-lg group hover:bg-gray-100 dark:text-white dark:hover:bg-gray-700" aria-controls="dropdown-example" data-collapse-toggle="dropdown-example">
                            <span className="flex-1 ms-3 text-left rtl:text-right whitespace-nowrap">Settings</span>
                        </button>
                    </li>
                    <li>
                        <button type="button" className="flex items-center w-full p-2 text-base text-gray-900 transition duration-75 rounded-lg group hover:bg-gray-100 dark:text-white dark:hover:bg-gray-700" aria-controls="dropdown-example" data-collapse-toggle="dropdown-example">
                            <span className="flex-1 ms-3 text-left rtl:text-right whitespace-nowrap">Email</span>
                        </button>
                    </li>
                    <li>
                        <a href="#" className="flex items-center p-2 text-gray-900 rounded-lg dark:text-white hover:bg-gray-100 dark:hover:bg-gray-700 group">
                        <span className="flex-1 ms-3 whitespace-nowrap" onClick={handleSignOut}>Logout</span>
                        </a>
                    </li>
                </ul>
            </div>
            </aside>
        </div>
    )
}

export default SideNav;