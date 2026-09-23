


// DoctorSelection.tsx
import React from 'react';
import { useMessage } from '../contexts/MessageContext';


const DoctorSelection: React.FC = () => {

    const {candidateDoctors, setDoctorChoice } = useMessage()

  if (!candidateDoctors || candidateDoctors.length === 0) {
    return null;
  }

  return (
    <div className="p-1 bg-gray-800/30 rounded-lg border border-gray-700 w-full">
      <h3 className="text-white font-semibold mb-3 text-sm w-full text-right" dir="auto">
        یک دکتر را انتخاب کنید.
      </h3>
      <div className="space-y-2 w-full">
        {candidateDoctors.map((doctor) => (
          <div key={doctor.id} className="flex relative flex-row-reverse items-center justify-between bg-gray-700/30 p-3 rounded w-full">
            <div className="text-right w-full">
              <div className="text-white text-sm font-medium">{doctor.name}</div>
              <hr className="border-gray-600 my-1" />
              <div className="text-gray-400 text-xs">{doctor.profession}</div>
              <div className="text-gray-400 text-xs">{doctor.hospital}</div>
            </div>
            <div className="absolute bottom-1 left-1 flex gap-1">
              <button 
                onClick={() => {
                  console.log("Cancel button clicked");
                  setDoctorChoice({
                    action: "cancel_booking"
                  });
                //   setCandidateDoctors([]); // Clear the box
                }}
                className="bg-gray-600 hover:bg-gray-700 text-white px-4 py-1.5 
                rounded text-xs transition-colors cursor-pointer"
              >
                انصراف
              </button>
              <button 
                onClick={() => {
                  console.log(`Button clicked for doctor: ${doctor.name} (ID: ${doctor.id})`);
                  setDoctorChoice({
                    action: "select_doctor",
                    doctor_id: doctor.id
                  });
                //   setCandidateDoctors([]); // Clear the box
                }}
                className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-1.5 
                rounded text-xs transition-colors cursor-pointer"
              >
                انتخاب این دکتر
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default DoctorSelection;