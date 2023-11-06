'use client'
import { useState } from 'react';
import { redirect } from 'next/navigation'
import { signIn } from 'next-auth/react';

// signOut, useSession
export default function page() {
    const [email, setEmail] = useState("");
    const [password, setPassword] = useState("");
    const [error, setError] = useState("");
    
    const handleSubmit = async (e) => {
        e.preventDefault();

        // built in nextAuth authentication for front-end.
        const res = await signIn("credentials", {
            email: email,
            password: password,
            redirect: false,
            callbackUrl: "/"
        });
        if (res?.error) {
            setError("Invalid Credentials");
            return;
        }

        // fetching login API to authenticate with backend Flask aswell.
        await fetch("http://127.0.0.1:5000/login", {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({email, password}),
        }).then(async res => {
            if (res?.ok) {
                const data = await res.json();
                console.log("response is ok", data)
            }
        }).catch(error => {
            console.error("Error in the flask login" + error);
        });

        // redirect user to login when all calls are successful.
        redirect("/");

        // if (restest.ok) {
        //     const data = await restest.json();
        //     console.log("restest is ok", data)
        // } else {
        //     const data = await restest.json();
        //     console.error("Error in the flask login" + data.error);
        // }
    };
    return (
        <section className='relative flex w-screen min-h-screen mx-auto items-center justify-center bg-bgLight'>
            
            {/*  Image on left testing before it was lg:w-1/2*/}
            <div className="w-full customBg h-screen z-0 opacity-40 md:min-h-screen md:opacity-100 lg:w-1/2 xl:w-full xl:z-10">
            </div>

            {/* Login Container */}
            <div className='absolute flex w-full min-h-screen items-center justify-center z-1 md:relative md:w-2/3 md:p-12 md:px-28 lg:w-2/3 xl:w-2/3'>
                {/* Login box */}
                <div className="flex justify-center items-center h-full bg-loginBoxLight customBorder
                                rounded-lg md:w-max-full lg:w-full xl:w-full xl:-translate-x-[45%]">
                    <div className="p-12 px-18 md:space-y-6">
                        <h1 className="flex flex-col text-white text-center font-extrabold text-4xl">
                            Journey AI
                        </h1>
                        
                        {/* Styles for form effect username and password text and input box */}
                        <form className="relative flex flex-col items-center px-8 pt-8 pb-10 space-y-7" action="#" onSubmit={handleSubmit}>
                            <div>
                                <label htmlFor="username" className="flex mb-2 text-sm font-bold text-white ">Username:</label>                        
                                <input type="username" name="username" id="username" className="bg-white border-solid border-[3px] border-borderColor 
                                focus:outline-none rounded-full block min-w-full py-2 px-4 text-gray-900 sm:text-sm md:w-[300px]" placeholder="Enter your Username..." required/>
                            </div>
                            <div>
                                <label htmlFor="password" className="flex mb-2 text-sm font-bold text-white">Password:</label>                        
                                {/* </div><input type="password" name="password" id="password" autoComplete="new-password" className="bg-white border text-gray-900 sm:text-sm rounded-lg focus:ring-primary-600 focus:border-primary-600 block w-full p-2.5" placeholder="password..." required/> */}
                                <input type="password" name="password" id="password" autoComplete="new-password" className="bg-white border-solid border-[3px] border-borderColor
                                focus:outline-none rounded-full block min-w-full py-2 px-4 text-gray-900 sm:text-sm md:w-[300px]" placeholder="Enter your Password..." required/>
                            </div>

                            {/* Login button */}
                            <div className="flex justify-center pt-2">
                                <button type="submit" className="flex w-[150px] justify-center items-center text-center bg-white  text-black hover:bg-bgLight 
                                rounded-lg text-sm font-bold px-5 py-2">
                                    Login
                                </button>
                            </div>

                            {/* Error message pops up for invalid credentials or any other errors */}
                            {error && (
                            <div className="bg-red-500 text-white w-fit text-sm py-1 px-3 rounded-md mt-2 mx-auto">
                                {error}
                            </div>
                            )}

                            {/* Register link */}
                            <div className="flex flex-col items-center justify-center text-sm font-bold text-white sm:pt-2 lg:flex-row lg:items-baseline">
                                Dont have an account? <a href="/register" className="flex items-center justify-centerfont-bold ml-2 text-[#8077FF] hover:underline md:ml-2 md:mt-0">Register here</a>
                            </div>

                            {/* Forgot password div */}
                            <div className="flex justify-center text-sm font-bold text-white">
                                <a href="/" className="font-medium text-primary-600 dark:text-primary-500 hover:text-bgLight">Forgot Password?</a>
                            </div>
                        </form>
                    </div>
                </div>
            </div>
        </section>
    );
}