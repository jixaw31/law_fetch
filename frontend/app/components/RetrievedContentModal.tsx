import { useMessage } from "../contexts/MessageContext";

const RetrievedContentModal = () => {
  const {
    retrievedContent,
    isRetrievedModalOpen,
    setIsRetrievedModalOpen,
  } = useMessage();

  if (!isRetrievedModalOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center" >
      <div
        className="absolute inset-0 bg-black/50"
        onClick={() => setIsRetrievedModalOpen(false)}
      />

      <div className="relative z-10 max-h-[80vh] w-[90%] max-w-3xl overflow-hidden rounded-xl bg-white shadow-xl dark:bg-gray-900">
        <div className="flex items-center justify-between border-b px-5 py-4">
          <h2 className="font-semibold">
            مستندات
          </h2>

          <button
            onClick={() => setIsRetrievedModalOpen(false)}
          >
            ×
          </button>
        </div>

        <div dir="auto" className="max-h-[70vh] overflow-y-auto whitespace-pre-wrap p-5">
          {retrievedContent}
        </div>
      </div>
    </div>
  );
};

export default RetrievedContentModal;