import React from 'react';
import { ToastContainer, toast } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';

// Create a function to display notifications
export const notify = (msg, type) => {
    switch (type) {
        case 'success':
            toast.success(msg);
            break;
        case 'warning':
            toast.warn(msg);
            break;
        case 'error':
            toast.error(msg);
            break;
        default:
            toast(msg); // Default toast
    }
};

// Create a ToastContainer component
const Toast = () => {
    return (
        <ToastContainer
            position="bottom-right"
            autoClose={2000}
            hideProgressBar={false}
            newestOnTop={false}
            closeOnClick
            rtl={false}
            pauseOnFocusLoss
            draggable
            pauseOnHover
            theme="light"
        />
    );
};

export default Toast;
