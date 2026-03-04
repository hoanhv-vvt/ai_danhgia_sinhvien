import React, { useState } from 'react';
import { Search, Loader2, Info, BookOpen, Building2, MapPin } from 'lucide-react';
import MajorResultCard, { MajorResultData } from './MajorResultCard';

// ----------- Mock data để xem trước UI -----------
const MOCK_RESULT: MajorResultData = {
    university: {
        name: 'Đại học RMIT Việt Nam',
        location: 'TP. Hồ Chí Minh',
        description:
            'RMIT Vietnam là trường đại học quốc tế uy tín với chương trình đào tạo chuẩn Úc, nằm trong top các trường tư thục hàng đầu tại Việt Nam.',
        rating: 'Top',
    },
    major: {
        name: 'Công nghệ thông tin',
        description:
            'Ngành CNTT tại RMIT được đánh giá rất cao với chương trình sát thực tế, nhiều cơ hội thực tập tại doanh nghiệp công nghệ lớn.',
        admissionYear: '2024',
        scoreScale: 30,
        calculatedScore100: 88,
        tuition: '280 - 330 triệu / năm',
        tuitionAvg: 310000000,
        rating: 'Top',
    },
    locationAnalysis: {
        region: 'urban',
        position: 'alley',
        estimatedValue: 'Cao — khu vực trung tâm Quận 5, tiếp cận nhiều tiện ích',
        riskAssessment:
            'Hẻm xe hơi rộng, khả năng thanh khoản tốt. Rủi ro thấp đến trung bình.',
        scoreModifier: 14,
    },
};

// ----------- State -----------
interface SearchState {
    universityQuery: string;
    majorQuery: string;
    addressQuery: string;
    isLoading: boolean;
    data: MajorResultData | null;
    error: string | null;
}

const UniversityMajorSearch: React.FC = () => {
    const [state, setState] = useState<SearchState>({
        universityQuery: '',
        majorQuery: '',
        addressQuery: '',
        isLoading: false,
        data: null,
        error: null,
    });

    // TODO: thay bằng gọi API thực tế
    const handleSearch = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!state.universityQuery.trim() || !state.majorQuery.trim()) return;

        setState(prev => ({ ...prev, isLoading: true, error: null, data: null }));

        // Giả lập delay gọi API
        await new Promise(res => setTimeout(res, 1200));

        // Trả về mock data (sau này thay bằng logic thực)
        setState(prev => ({ ...prev, isLoading: false, data: MOCK_RESULT }));
    };

    const canSearch = state.universityQuery.trim() && state.majorQuery.trim() && !state.isLoading;

    return (
        <div className="animate-fade-in">
            {/* ── TIÊU ĐỀ ── */}
            <section className="text-center mb-10">
                <h2 className="text-2xl md:text-3xl font-extrabold text-slate-900 mb-3">
                    Tra cứu Trường &amp; Ngành học
                </h2>
                <p className="text-slate-500 mb-6 max-w-xl mx-auto text-sm md:text-base">
                    Nhập tên trường và ngành học để xem điểm chuẩn, học phí và phân tích địa chỉ tài sản.
                </p>
            </section>

            {/* ── FORM ── */}
            <form onSubmit={handleSearch} className="max-w-2xl mx-auto space-y-3 mb-8">
                {/* Input: Tên trường */}
                <div className="relative group">
                    <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
                        <Building2 className="h-5 w-5 text-gray-400 group-focus-within:text-indigo-500 transition-colors" />
                    </div>
                    <input
                        id="university-input"
                        type="text"
                        className="block w-full pl-11 pr-4 py-3 bg-white border border-gray-200 rounded-xl text-base shadow-sm placeholder-gray-400 focus:outline-none focus:ring-4 focus:ring-indigo-500/10 focus:border-indigo-500 transition-all"
                        placeholder="Tên trường — VD: Đại học RMIT Việt Nam"
                        value={state.universityQuery}
                        onChange={e => setState(prev => ({ ...prev, universityQuery: e.target.value }))}
                        disabled={state.isLoading}
                    />
                </div>

                {/* Input: Ngành học */}
                <div className="relative group">
                    <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
                        <BookOpen className="h-5 w-5 text-gray-400 group-focus-within:text-violet-500 transition-colors" />
                    </div>
                    <input
                        id="major-input"
                        type="text"
                        className="block w-full pl-11 pr-4 py-3 bg-white border border-gray-200 rounded-xl text-base shadow-sm placeholder-gray-400 focus:outline-none focus:ring-4 focus:ring-violet-500/10 focus:border-violet-500 transition-all"
                        placeholder="Ngành học — VD: Công nghệ thông tin"
                        value={state.majorQuery}
                        onChange={e => setState(prev => ({ ...prev, majorQuery: e.target.value }))}
                        disabled={state.isLoading}
                    />
                </div>

                {/* Input: Địa chỉ (tùy chọn) */}
                <div className="relative group">
                    <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
                        <MapPin className="h-5 w-5 text-gray-400 group-focus-within:text-emerald-500 transition-colors" />
                    </div>
                    <input
                        id="address-input"
                        type="text"
                        className="block w-full pl-11 pr-4 py-3 bg-white border border-gray-200 rounded-xl text-base shadow-sm placeholder-gray-400 focus:outline-none focus:ring-4 focus:ring-emerald-500/10 focus:border-emerald-500 transition-all"
                        placeholder="Địa chỉ tài sản (không bắt buộc) — VD: Hẻm 125 Nguyễn Văn Cừ, Q.5"
                        value={state.addressQuery}
                        onChange={e => setState(prev => ({ ...prev, addressQuery: e.target.value }))}
                        disabled={state.isLoading}
                    />
                </div>

                {/* Nút tra cứu */}
                <button
                    id="search-button"
                    type="submit"
                    disabled={!canSearch}
                    className="w-full flex items-center justify-center gap-2 bg-indigo-600 hover:bg-indigo-700 active:bg-indigo-800 text-white font-semibold rounded-xl px-6 py-3 transition-all shadow-sm disabled:opacity-50 disabled:cursor-not-allowed"
                >
                    {state.isLoading ? (
                        <>
                            <Loader2 className="h-4 w-4 animate-spin" />
                            Đang tra cứu...
                        </>
                    ) : (
                        <>
                            <Search className="h-4 w-4" />
                            Tra cứu
                        </>
                    )}
                </button>
            </form>

            {/* ── KẾT QUẢ ── */}
            <div className="space-y-6 min-h-[200px]">
                {/* Legend khi chưa có kết quả */}
                {!state.data && !state.isLoading && !state.error && (
                    <div className="grid grid-cols-2 md:grid-cols-5 gap-3 max-w-3xl mx-auto mt-4 opacity-60">
                        {[
                            { range: '> 90', label: 'Top', color: 'text-purple-600' },
                            { range: '80–89', label: 'Tốt', color: 'text-green-600' },
                            { range: '70–79', label: 'Khá', color: 'text-blue-600' },
                            { range: '50–69', label: 'TB', color: 'text-yellow-600' },
                            { range: '< 50', label: 'Kém', color: 'text-red-600' },
                        ].map(item => (
                            <div key={item.label} className="flex flex-col items-center p-2 bg-white rounded border shadow-sm">
                                <span className={`font-bold ${item.color}`}>{item.range}</span>
                                <span className="text-[10px] uppercase font-bold text-gray-400">{item.label}</span>
                            </div>
                        ))}
                    </div>
                )}

                {/* Loading skeleton */}
                {state.isLoading && (
                    <div className="w-full bg-white rounded-2xl shadow-sm border border-gray-100 p-8 animate-pulse">
                        <div className="h-8 bg-gray-200 rounded w-1/2 mb-4" />
                        <div className="h-4 bg-gray-200 rounded w-1/4 mb-10" />
                        <div className="grid grid-cols-3 gap-6">
                            <div className="h-40 bg-gray-200 rounded-xl" />
                            <div className="col-span-2 space-y-3">
                                <div className="h-16 bg-gray-200 rounded-xl" />
                                <div className="h-10 bg-gray-200 rounded-xl" />
                                <div className="h-10 bg-gray-200 rounded-xl" />
                            </div>
                        </div>
                    </div>
                )}

                {/* Lỗi */}
                {state.error && (
                    <div className="bg-red-50 border border-red-200 rounded-xl p-4 flex items-start gap-3 text-red-700 max-w-2xl mx-auto">
                        <Info className="h-5 w-5 flex-shrink-0 mt-0.5" />
                        <p>{state.error}</p>
                    </div>
                )}

                {/* Kết quả */}
                {state.data && !state.isLoading && (
                    <MajorResultCard data={state.data} />
                )}
            </div>
        </div>
    );
};

export default UniversityMajorSearch;
