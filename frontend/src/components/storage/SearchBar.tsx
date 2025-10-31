import React, { useState } from "react";
import { IoSearch } from "react-icons/io5";
import { FaSortAmountDown, FaSortAmountUp } from "react-icons/fa";

const SearchBar: React.FC = () => {
    const [sortOrder, setSortOrder] = useState<"asc" | "desc">("asc");

    const toggleSort = () => {
        setSortOrder(prev => (prev === "asc" ? "desc" : "asc"));
    };

    return (
        <div className="relative w-full flex flex-row gap-2 items-center">
            {/* Search Input */}
            <div className="w-full relative">
                <IoSearch className="absolute left-4 top-1/2 -translate-y-1/2 text-secondary-text text-xl" />
                <input
                    type="text"
                    placeholder="Search"
                    className="w-full bg-second-background text-secondary-text placeholder-gray-500 rounded-2xl py-3 pl-12 pr-4 focus:outline-none focus:ring-2 focus:ring-gray-600 transition-all"
                />
            </div>

            {/* Sort Button */}
            <button
                onClick={toggleSort}
                className="flex items-center justify-center px-4 py-3 bg-second-background rounded-2xl hover:bg-third-background transition-all text-secondary-text focus:outline-none focus:ring-2 focus:ring-gray-600"
                title={`Sort ${sortOrder === "asc" ? "Descending" : "Ascending"}`}
            >
                {sortOrder === "asc" ? (
                    <FaSortAmountDown className="text-xl" />
                ) : (
                    <FaSortAmountUp className="text-xl" />
                )}
            </button>
        </div>
    );
};

export default SearchBar;