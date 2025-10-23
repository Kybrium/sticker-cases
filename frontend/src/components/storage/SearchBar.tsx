import { IoSearch } from "react-icons/io5";

const SearchBar: React.FC = () => {
    return (
        <div className="relative w-full">
            <IoSearch className="absolute left-4 top-1/2 -translate-y-1/2 text-secondary-text text-xl" />
            <input
                type="text"
                placeholder="Search"
                className="w-full bg-second-background text-secondary-text placeholder-gray-500 rounded-2xl py-3 pl-12 pr-4 focus:outline-none focus:ring-2 focus:ring-gray-600 transition-all"
            />
        </div>
    );
};

export default SearchBar;