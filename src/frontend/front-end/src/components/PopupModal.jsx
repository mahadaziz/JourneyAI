'use client'
import React, { useState, useEffect } from 'react'
import Image from 'next/image'


const PopupModal = ({ isModalOpen, closeModal }) => {
    const [visibility, setVisibility] = useState('hidden')
    
    useEffect(() => {
        let timeoutId
    
        if (!isModalOpen) {
            timeoutId = setTimeout(() => {
                setVisibility('hidden')
            }, 300)
        } else {
            setVisibility('visible')
        }
    
        return () => clearTimeout(timeoutId)
    }, [isModalOpen])

    const modalBackgroundStyle = isModalOpen
    ? {
        visibility: visibility,
        opacity: 1,
        transform: 'scale(1)',
        transition: 'opacity 0.3s ease, transform 0.3s ease'
    }
    : {
        visibility: visibility,
        opacity: 0,
        transform: 'scale(0.95)',
        transition: 'opacity 0.3s ease, transform 0.3s ease',
        pointerEvents: 'none'
    }

    const handleModalClick = (e) => {
        e.stopPropagation()
    }

    return (
        <div id="popup-modal" tabIndex="-1" onClick={closeModal} style={modalBackgroundStyle} className="overflow-y-auto overflow-x-hidden fixed top-0 right-0 left-0 bottom-0 z-50 flex justify-center items-center w-screen h-screen">
            <div className="relative p-4 w-full h-full max-w-[90vw] max-h-[90vh]" onClick={handleModalClick}>
                <div className="relative flex justify-center items-center bg-white rounded-lg shadow dark:bg-gray-700">
                    <div className="flex justify-center items-center overflow-auto p-4 md:p-5">
                        {/* <h3 className="mb-5 text-lg font-normal text-gray-500 dark:text-gray-400">Graph goes here</h3> */}
                        <Image src="/chart.png" layout='responsive' width={1000} height={2000} objectFit='contain' alt="Modal Content" />
                    </div>
                </div>
            </div>
        </div>
    )
}

export default PopupModal
