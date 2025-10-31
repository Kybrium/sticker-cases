import { BsThreeDotsVertical } from "react-icons/bs";

const Stickers: React.FC<{ data: any }> = ({ data }) => {
    return (
        <div className="w-full grid grid-cols-3 space-y-2 gap-2 mt-6">
            {data.map((pack: any) =>
                <div key={pack.id} className="flex flex-col items-center">
                    <div className="bg-second-background rounded-2xl relative">
                        <p className="absolute left-1 top-1 px-1 text-white text-xs bg-additional-bg/50 rounded-2xl">Sticker Pack</p>
                        <BsThreeDotsVertical className="absolute right-1 bottom-1 px-1 text-white text-2xl bg-additional-bg/50 rounded-2xl" />
                        <img src={pack.image_url} />
                    </div>
                    <p className="text-primary-text/80 font-bold">{pack.pack_name}</p>
                    <p className="text-primary-text/80 text-sm font-extralight flex flex-row gap-2 items-center bg-third-background px-2 py-1 rounded-2xl">{pack.floor_price.toFixed(2)}<img src='https://ton.org/download/ton_symbol.png' className="object-cover w-4 h-4 rounded-full" /></p>
                </div>
            )}
        </div>
    )
}

export default Stickers;