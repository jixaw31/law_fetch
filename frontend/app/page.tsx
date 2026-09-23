
import Link from "next/link";
export default function Home() {
  // const [isFixed, setIsFixed] = useState(false);

  // useEffect(() => {
  //   const handleScroll = () => {
  //     if (window.scrollY > 100) {
  //       setIsFixed(true);
  //     } else {
  //       setIsFixed(false);
  //     }
  //   };

  //   window.addEventListener("scroll", handleScroll);
  //   return () => window.removeEventListener("scroll", handleScroll);
  // }, []);

  return (
    <div className="h-[200vh] mt-15"> {/* extra height just to scroll */}
      <div className="h-75 text-gray-400 flex flex-col justify-center items-center">
        <h1 className="font-bold text-3xl text-gray-200 mb-6">What service we provide</h1>
        <p>Lorem ipsum dolor sit amet consectetur adipisicing elit. Dolor, ea?</p>
        <hr className="my-4 border-t border-gray-300 min-w-100" />
        <p>Lorem ipsum dolor sit amet consectetur adipisicing elit. Dolor, ea?</p>
                <hr className="my-4 border-t border-gray-300 min-w-100" />
        <p>Lorem ipsum dolor sit amet consectetur adipisicing elit. Dolor, ea?</p>
                <hr className="my-4 border-t border-gray-300 min-w-100" />
        <p>Lorem ipsum dolor sit amet consectetur adipisicing elit. Dolor, ea?</p>
      </div>

      <div className="flex justify-center gap-4 mt-6">
        <Link
          href="/general/new"
          className="px-6 py-3 bg-gray-400 text-gray-900 font-bold text-lg rounded hover:bg-gray-100 transition-all ease-in-out text-center"
        >
          WRONG TO SHOW THIS PAGE AFTER LOGIN
        </Link>
        
        
      </div>
    </div>
  );
}