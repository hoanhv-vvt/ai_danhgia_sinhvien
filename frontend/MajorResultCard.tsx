// ----------- Types (mirrors danhgia_truong_nganh.py output) -----------
type Rating = 'Top' | 'Tốt' | 'Khá' | 'Trung bình' | 'Kém';
type Region = 'urban' | 'suburban' | 'rural';
type Position = 'main_street' | 'alley' | 'deep_alley';

export interface MajorResultData {
    university: {
        name: string;
        location: string;
        description?: string;
        rating: Rating;
    };
    major: {
        name: string;
        description?: string;
        admissionYear?: string;
        scoreScale?: number;
        calculatedScore100: number;
        tuition?: string;
        tuitionAvg: number;
        rating: Rating;
    };
    locationAnalysis?: {
        region: Region;
        position: Position;
        estimatedValue: string;
        riskAssessment: string;
        scoreModifier?: number;
    } | null;
}

// ----------- Lookup maps -----------
const RATING_STYLE: Record<Rating, string> = {
    Top: 'bg-purple-100 text-purple-700 border-purple-200',
    Tốt: 'bg-green-100 text-green-700 border-green-200',
    Khá: 'bg-blue-100 text-blue-700 border-blue-200',
    'Trung bình': 'bg-yellow-100 text-yellow-800 border-yellow-200',
    Kém: 'bg-red-100 text-red-700 border-red-200',
};

const RATING_BADGE: Record<Rating, string> = {
    Top: '🏆 Top Tier',
    Tốt: '✨ Tốt',
    Khá: '👍 Khá',
    'Trung bình': '⚖️ Trung bình',
    Kém: '⚠️ Kém',
};

const REGION_LABEL: Record<Region, string> = {
    urban: '🏙️ Trung tâm TP',
    suburban: '🏘️ Ngoại ô / Huyện',
    rural: '🌾 Nông thôn / Tỉnh lẻ',
};

const POSITION_LABEL: Record<Position, string> = {
    main_street: '🛣️ Mặt tiền đường lớn',
    alley: '↪️ Hẻm xe hơi',
    deep_alley: '🚫 Hẻm sâu / Hẻm cụt',
};

const SCORE_BAR_COLOR: Record<Rating, string> = {
    Top: 'bg-purple-500',
    Tốt: 'bg-green-500',
    Khá: 'bg-blue-500',
    'Trung bình': 'bg-yellow-400',
    Kém: 'bg-red-500',
};

// ----------- ScoreBar sub-component -----------
interface ScoreBarProps { score: number; rating: Rating; }

function ScoreBar({ score, rating }: ScoreBarProps) {
    return (
        <div className="w-full">
            <div className="flex justify-between text-xs text-gray-400 mb-1">
                <span>0</span>
                <span className="font-bold text-gray-700 text-base">{score.toFixed(0)} / 100</span>
                <span>100</span>
            </div>
            <div className="w-full h-3 bg-gray-200 rounded-full overflow-hidden">
                <div
                    className={`h-full rounded-full transition-all duration-700 ${SCORE_BAR_COLOR[rating]}`}
                    style={{ width: `${Math.min(score, 100)}%` }}
                />
            </div>
        </div>
    );
}

// ----------- Main Component -----------
interface Props { data: MajorResultData; }

export default function MajorResultCard({ data }: Props) {
    const { university, major, locationAnalysis } = data;

    return (
        <div className="bg-white rounded-2xl shadow-xl overflow-hidden border border-gray-100">

            {/* ── HEADER: Tên trường ── */}
            <div className="bg-gradient-to-r from-indigo-600 to-violet-700 p-6 text-white">
                <div className="flex justify-between items-start flex-wrap gap-3">
                    <div>
                        <h2 className="text-2xl font-bold mb-1">{university.name}</h2>
                        <div className="flex items-center gap-2 text-indigo-200 text-sm">
                            <span>📍</span>
                            <span>{university.location}</span>
                        </div>
                    </div>
                    <span className={`px-3 py-1 rounded-lg text-sm font-bold border shadow-sm bg-white/90 ${RATING_STYLE[university.rating]}`}>
                        Trường: {RATING_BADGE[university.rating]}
                    </span>
                </div>
            </div>

            <div className="p-6 space-y-8">

                {/* ── NGÀNH HỌC ── */}
                <section>
                    <div className="flex items-center gap-2 mb-4 flex-wrap">
                        <span className="text-violet-500">🎓</span>
                        <h3 className="text-lg font-bold text-gray-800">Ngành: {major.name}</h3>
                        <span className={`ml-auto px-3 py-0.5 rounded-full text-xs font-bold border ${RATING_STYLE[major.rating]}`}>
                            {RATING_BADGE[major.rating]}
                        </span>
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                        {/* Cột trái: điểm chuẩn */}
                        <div className="col-span-1 flex flex-col items-center justify-center gap-4 p-5 bg-gray-50 rounded-xl border border-gray-100">
                            <div className="text-center">
                                <div className="text-3xl mb-1">📊</div>
                                <p className="text-xs text-gray-400 uppercase tracking-wide">Điểm chuẩn ngành (thang 100)</p>
                            </div>
                            <ScoreBar score={major.calculatedScore100} rating={major.rating} />
                            <span className={`text-sm font-bold px-3 py-1 rounded-full border ${RATING_STYLE[major.rating]}`}>
                                {major.rating}
                            </span>
                        </div>

                        {/* Cột phải: chi tiết */}
                        <div className="col-span-1 md:col-span-2 space-y-4">
                            {/* Học phí */}
                            <div className="bg-green-50 rounded-xl p-4 border border-green-100 flex items-start gap-3">
                                <div className="bg-white p-2 rounded-lg shadow-sm text-green-600 shrink-0 text-xl">💵</div>
                                <div>
                                    <p className="text-xs font-bold uppercase text-green-700 tracking-wider mb-1">Học phí ngành (ước tính)</p>
                                    <p className="font-semibold text-green-900 text-base">
                                        {major.tuition || `${(major.tuitionAvg / 1_000_000).toFixed(0)} triệu / năm`}
                                    </p>
                                    <p className="text-[10px] text-green-600/80 mt-0.5">
                                        * Số liệu tham khảo, có thể thay đổi theo năm học.
                                    </p>
                                </div>
                            </div>

                            {/* Mô tả ngành */}
                            {major.description && (
                                <p className="text-sm text-gray-600 leading-relaxed bg-gray-50 rounded-lg p-3 border border-gray-100">
                                    {major.description}
                                </p>
                            )}

                            {/* Năm & thang điểm */}
                            <div className="grid grid-cols-2 gap-3 text-sm">
                                <div className="bg-indigo-50 rounded-lg p-3 border border-indigo-100">
                                    <p className="text-xs text-indigo-400 font-semibold uppercase tracking-wide mb-1">Năm dữ liệu</p>
                                    <p className="font-bold text-indigo-700">{major.admissionYear ?? 'Mới nhất'}</p>
                                </div>
                                <div className="bg-indigo-50 rounded-lg p-3 border border-indigo-100">
                                    <p className="text-xs text-indigo-400 font-semibold uppercase tracking-wide mb-1">Thang điểm gốc</p>
                                    <p className="font-bold text-indigo-700">{major.scoreScale ?? 30}</p>
                                </div>
                            </div>
                        </div>
                    </div>
                </section>

                {/* ── TỔNG QUAN TRƯỜNG ── */}
                {university.description && (
                    <section className="border-t border-gray-100 pt-6">
                        <div className="flex items-center gap-2 mb-2">
                            <span className="text-indigo-400">🏫</span>
                            <h3 className="text-sm font-bold text-gray-600 uppercase tracking-wide">Tổng quan trường</h3>
                        </div>
                        <p className="text-gray-600 text-sm leading-relaxed">{university.description}</p>
                    </section>
                )}

                {/* ── PHÂN TÍCH ĐỊA CHỈ ── */}
                {locationAnalysis && (
                    <section className="border-t border-gray-100 pt-6">
                        <div className="flex items-center gap-2 mb-4">
                            <span className="text-emerald-500">🏠</span>
                            <h3 className="text-sm font-bold text-gray-600 uppercase tracking-wide">Phân tích địa chỉ tài sản</h3>
                        </div>
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                            {/* Tags + giá trị ước tính */}
                            <div className="space-y-3">
                                <div className="flex flex-wrap gap-2">
                                    <span className="px-3 py-1 rounded-full text-xs font-semibold bg-blue-100 text-blue-700 border border-blue-200">
                                        {REGION_LABEL[locationAnalysis.region]}
                                    </span>
                                    <span className="px-3 py-1 rounded-full text-xs font-semibold bg-orange-100 text-orange-700 border border-orange-200">
                                        {POSITION_LABEL[locationAnalysis.position]}
                                    </span>
                                </div>
                                <div className="bg-gray-50 rounded-lg p-3 border border-gray-100">
                                    <p className="text-xs font-semibold text-gray-500 uppercase tracking-wide mb-1">Giá trị ước tính</p>
                                    <p className="text-sm font-bold text-gray-800">{locationAnalysis.estimatedValue}</p>
                                    {locationAnalysis.scoreModifier !== undefined && (
                                        <p className="text-xs text-indigo-500 mt-1">
                                            Điểm vị trí: <span className="font-bold">+{locationAnalysis.scoreModifier}</span>
                                        </p>
                                    )}
                                </div>
                            </div>
                            {/* Rủi ro */}
                            <div className="bg-amber-50 rounded-lg p-4 border border-amber-100">
                                <p className="text-xs font-semibold text-amber-600 uppercase tracking-wide mb-2">Đánh giá rủi ro</p>
                                <p className="text-sm text-amber-800 leading-relaxed">{locationAnalysis.riskAssessment}</p>
                            </div>
                        </div>
                    </section>
                )}

            </div>
        </div>
    );
}
