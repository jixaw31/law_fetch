'use client';

import { useState } from 'react';
import { useCareerMatchesContext } from '../contexts/CareerContext';
import { useUser } from '../contexts/AuthContext';

const MatchProfilesModal: React.FC = () => {
  const [showModal, setShowModal] = useState(false);
  const { matches, fetchMatches, isLoading, error } = useCareerMatchesContext();
  const { user } = useUser();

  const handleFetch = async () => {
    if (!user) return;
    await fetchMatches(user.id);
    setShowModal(true);
  };

  return (
    <>
      <div className="fixed top-2 left-20 z-50 flex items-center space-x-2">
        <button
        className="bg-slate-500 text-black font-bold rounded p-2 
                  hover:bg-slate-300 transition cursor-pointer"
        onClick={handleFetch}
        disabled={isLoading}
      >
        Show Potential Colleagues
        <span className="block text-[10px]">
          as tool?
        </span>
      </button>

  {isLoading && (
    <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
  )}
</div>

      {/* Modal Overlay */}
      {showModal && (
      <div
        className="fixed inset-0 bg-black/50 flex items-center justify-center z-50"
        onClick={() => setShowModal(false)}
      >
        <div
          className="bg-gray-700 rounded-lg shadow-lg w-[400px] max-h-[80vh] 
                    overflow-y-auto p-4 relative"
          onClick={(e) => e.stopPropagation()}
        >
          <button
            className="absolute px-2 rounded cursor-pointer top-2 right-2 
                      text-xl font-bold text-dark hover:text-gray-900
                      hover:bg-gray-500"
            onClick={() => setShowModal(false)}
          >
            ×
          </button>
          <h2 className="text-lg font-semibold mb-4">Matched Profiles</h2>

          {isLoading && (
            <div className="flex justify-center items-center py-10">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-white"></div>
              <span className="ml-2 text-white">Loading...</span>
            </div>
          )}

          {!isLoading && error && <p className="text-red-600">{error}</p>}
          {!isLoading && !error && matches.length === 0 && <p>No matches found</p>}

          {!isLoading && matches.length > 0 && (
            <div className="space-y-3">
              {matches.map((m, idx) => (
              <div
                key={idx}
                className="p-2 bg-gray-900 border border-gray-300 
                          rounded shadow-sm transition"
              >
                <div className="flex justify-between items-stretch">
                  {/* Left side */}
                  <div className="flex flex-col">
                    <p><strong>User Name:</strong> {m.user_name}</p>
                    <p><strong>Similarity:</strong> {(m.similarity * 100).toFixed(2)}%</p>
                    {m.phone_number && <p><strong>Phone:</strong> {m.phone_number}</p>}
                    {(m.city || m.country) && (
                      <p><strong>Location:</strong> {m.city ?? ''} {m.country ?? ''}</p>
                    )}
                  </div>

                  {/* Right side — two buttons vertically */}
                  <div className="flex flex-col justify-between ml-4">
                    <button
                      onClick={() => {
                        console.log("send message", m.user_name);
                      }}
                      className="px-3 py-1 text-sm rounded bg-blue-700 hover:bg-blue-500 
                                min-h-12 cursor-pointer"
                    >
                      Send Message
                    </button>

                    <button
                      onClick={() => {
                        console.log("connection request sent to:", m.user_name);
                      }}
                      className="mt-2 px-3 py-1 text-sm rounded bg-gray-500 hover:bg-gray-400 
                                min-h-12 cursor-pointer"
                    >
                      Connect
                    </button>
                  </div>
                </div>
              </div>
            ))}

            </div>
          )}
        </div>
      </div>
    )}

    </>
  );
};

export default MatchProfilesModal;
