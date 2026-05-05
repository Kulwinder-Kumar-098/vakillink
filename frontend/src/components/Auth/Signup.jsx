import React, { useState } from 'react';

export default function Signup() {
  const [formData, setFormData] = useState({
    fullName: '',
    email: '',
    password: '',
    role: 'user', // Default role
    // Fields specifically for lawyers
    barCouncilId: '',
    experienceYears: ''
  });

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    // TODO: Connect to backend /api/v1/auth/signup
    console.log("Submitting Signup Data:", formData);
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-md w-full space-y-8 bg-white p-8 rounded-xl shadow-md">
        <div>
          <h2 className="mt-6 text-center text-3xl font-extrabold text-gray-900">
            Create your VakeelLink account
          </h2>
        </div>
        <form className="mt-8 space-y-6" onSubmit={handleSubmit}>
          <div className="rounded-md shadow-sm space-y-4">
            
            {/* Role Selection Dropdown */}
            <div>
              <label htmlFor="role" className="block text-sm font-medium text-gray-700">I am joining as a</label>
              <select
                id="role"
                name="role"
                value={formData.role}
                onChange={handleChange}
                className="mt-1 block w-full pl-3 pr-10 py-2 text-base border border-gray-300 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm rounded-md"
              >
                <option value="user">Client (Seeking Legal Help)</option>
                <option value="lawyer">Lawyer (Providing Legal Help)</option>
                <option value="admin">Administrator</option>
              </select>
            </div>

            {/* Common Fields */}
            <div>
              <label className="block text-sm font-medium text-gray-700">Full Name</label>
              <input name="fullName" type="text" required onChange={handleChange}
                className="appearance-none rounded-md relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm" placeholder="John Doe" />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700">Email Address</label>
              <input name="email" type="email" required onChange={handleChange}
                className="appearance-none rounded-md relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm" placeholder="john@example.com" />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700">Password</label>
              <input name="password" type="password" required onChange={handleChange}
                className="appearance-none rounded-md relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm" placeholder="••••••••" />
            </div>

            {/* Conditional Fields for Lawyers */}
            {formData.role === 'lawyer' && (
              <div className="space-y-4 p-4 bg-blue-50 rounded-md border border-blue-100">
                <p className="text-sm text-blue-800 font-medium mb-2">Lawyer Verification Details</p>
                <div>
                  <label className="block text-sm font-medium text-gray-700">Bar Council ID</label>
                  <input name="barCouncilId" type="text" required onChange={handleChange}
                    className="appearance-none rounded-md relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm" placeholder="e.g., UP/1234/2020" />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700">Years of Experience</label>
                  <input name="experienceYears" type="number" min="0" required onChange={handleChange}
                    className="appearance-none rounded-md relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm" placeholder="e.g., 5" />
                </div>
              </div>
            )}
            
            {/* Conditional Field for Admins */}
            {formData.role === 'admin' && (
               <div className="space-y-4 p-4 bg-red-50 rounded-md border border-red-100">
                 <p className="text-sm text-red-800 font-medium mb-2">Admin Registration</p>
                 <p className="text-xs text-red-600">Your account will be placed in a pending state. You will not have access to the Admin Portal until approved by a Super Admin.</p>
               </div>
            )}

          </div>

          <div>
            <button type="submit" className="group relative w-full flex justify-center py-2 px-4 border border-transparent text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500">
              Sign Up
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
