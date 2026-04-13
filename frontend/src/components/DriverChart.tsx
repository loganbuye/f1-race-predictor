import type { DriverHistory } from "../types";

interface Props {
    history: DriverHistory;
    driverName: string;
}

export default function DriverChart({ history, driverName }: Props) {
    const { finish_history, avg_finish, races } = history;
    const max = 20;

    return (
        <div className="bg-white/5 rounded-xl p-5 mt-4">
            <div className="flex justify-between items-center mb-4">
                <h3 className="text-white font-bold text-lg">{driverName} - Recent Form</h3>
                <div className="text-right">
                    <span className="text-white font-bold">{avg_finish.toFixed(1)}</span>
                    <p className="text-white/50 text-xs">avg finish</p>
                </div>
            </div>

            {/* Bar Chart */}
            <div className="flex items-end gap-1.5 h-32">
                {finish_history.map((pos, i) => {
                    const height = ((max - pos) / (max - 1)) * 100;
                    const isTop10 = pos <= 10;
                    return (
                        <div key={i} className="flex-1 flex flex-col items-center gap-1">
                            <span className="text-white/50 text-xs">{pos}</span>
                            <div 
                            className="w-full rounded-t transition-all duration-300"
                            style={{
                                height: `${height}%`,
                                backgroundColor: isTop10 ? "ff#8000" : "#ffffff30",
                                minHeight: "4px"
                            }}
                            />
                        </div>
                    );
                })}
            </div>
            
            <div className="flex justify-between mt-2 text-white/30 text-xs">
                <span>Oldest</span>
                <span>{races} races</span>
                <span>Latest</span>
            </div>
        </div>

        
    )
}