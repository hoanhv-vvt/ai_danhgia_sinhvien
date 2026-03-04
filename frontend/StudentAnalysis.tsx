
import React, { useState } from 'react';
import { Loader2, Info, Calculator, CheckCircle2, XCircle, AlertTriangle, GraduationCap, TrendingUp, MapPin } from 'lucide-react';
import { fetchUniversityData } from '../services/geminiService';
import { getScoringConfig } from '../services/configService';
import { UniversityData, StudentProfile } from '../types';
import ResultCard from './ResultCard';

// --- Utility: Đọc số tiền thành chữ (Vietnamese) ---
const docSo3ChuSo = (baso: number) => {
  const chuSo = ["không", "một", "hai", "ba", "bốn", "năm", "sáu", "bảy", "tám", "chín"];
  const tram = Math.floor(baso / 100);
  const chuc = Math.floor((baso % 100) / 10);
  const donvi = baso % 10;
  let ketqua = "";

  if (tram === 0 && chuc === 0 && donvi === 0) return "";

  if (tram !== 0) {
    ketqua += chuSo[tram] + " trăm ";
    if (chuc === 0 && donvi !== 0) ketqua += "linh ";
  }

  if (chuc !== 0 && chuc !== 1) {
    ketqua += chuSo[chuc] + " mươi";
    if (chuc === 0 && donvi !== 0) ketqua = ketqua + " linh ";
  }

  if (chuc === 1) ketqua += "mười";

  switch (donvi) {
    case 1:
      if (chuc !== 0 && chuc !== 1) ketqua += " mốt";
      else ketqua += " một";
      break;
    case 5:
      if (chuc === 0) ketqua += " năm";
      else ketqua += " lăm";
      break;
    default:
      if (donvi !== 0) ketqua += " " + chuSo[donvi];
      break;
  }
  return ketqua;
}

const docSoTien = (soTien: number): string => {
  if (soTien === 0) return "Không đồng";
  const tien = ["", " nghìn", " triệu", " tỷ", " nghìn tỷ", " triệu tỷ"];
  let lan = 0;
  let i = 0;
  let so = soTien;
  let ketqua = "";
  let tmp = "";
  let vitri = [];

  if (so < 0) return "Số tiền âm";
  if (so > 0) {
    so = Math.abs(so);
  }

  // Tách số thành các nhóm 3 chữ số
  while (so > 0) {
    vitri[lan] = so % 1000;
    so = Math.floor(so / 1000);
    lan++;
  }

  if (lan > 0) {
    // Đọc từng nhóm
    for (i = lan - 1; i >= 0; i--) {
      tmp = docSo3ChuSo(vitri[i]);
      ketqua += tmp;
      if (vitri[i] > 0) ketqua += tien[i];
      // Thêm dấu phẩy nếu chưa kết thúc và nhóm sau không rỗng
      if ((i > 0) && (tmp.length > 0)) ketqua += ",";
    }
  }

  // Chuẩn hóa văn bản
  ketqua = ketqua.replace(/,$/, ''); // Xóa dấu phẩy cuối
  ketqua = ketqua.trim();

  // Viết hoa chữ cái đầu
  return ketqua.charAt(0).toUpperCase() + ketqua.slice(1) + " đồng";
};

const StudentAnalysis: React.FC = () => {
  const [profile, setProfile] = useState<StudentProfile>({
    loanAmount: 10000000,
    universityName: '',
    address: '',
    phoneType: 'normal',
    parentsJob: 'noInfo',
    socialMedia: 'none',
    pcb: 'none',
    consistency: 'reasonable'
  });

  const [isLoading, setIsLoading] = useState(false);
  const [uniData, setUniData] = useState<UniversityData | null>(null);
  const [finalScore, setFinalScore] = useState<number | null>(null);
  const [recommendation, setRecommendation] = useState<'APPROVE' | 'REJECT' | 'REVIEW' | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [scoreBreakdown, setScoreBreakdown] = useState<string[]>([]);

  // Handle number input change with formatting
  const handleLoanAmountChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    // Remove all non-digit characters
    const rawValue = e.target.value.replace(/\D/g, '');

    // Parse to integer or 0
    const numericValue = rawValue ? parseInt(rawValue, 10) : 0;

    setProfile({ ...profile, loanAmount: numericValue });
  };

  // Format display value with dots
  const displayLoanAmount = profile.loanAmount === 0 ? '' : new Intl.NumberFormat('vi-VN').format(profile.loanAmount);

  const handleAnalyze = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!profile.universityName.trim()) {
      setError("Vui lòng nhập tên trường đại học");
      return;
    }

    setIsLoading(true);
    setError(null);
    setUniData(null);
    setFinalScore(null);
    setRecommendation(null);
    setScoreBreakdown([]);

    try {
      // 1. Fetch University & Address Data (AI)
      const data = await fetchUniversityData(profile.universityName, profile.address);
      setUniData(data);

      // 2. Load Config
      const config = getScoringConfig();
      const logs: string[] = [];

      // 3. Calculate Score
      let score = config.baseScore;

      // -- University Component --
      const uniPoints = data.calculatedScore100 * config.universityWeight;
      score += uniPoints;
      logs.push(`Điểm trường học (${data.calculatedScore100} x ${config.universityWeight}): +${uniPoints.toFixed(1)}`);

      // -- Financial Safety Factor (Loan vs Tuition & Absolute Amount) --
      if (data.tuitionAvg > 0) {
        const ratio = profile.loanAmount / data.tuitionAvg;
        const ratioPercent = (ratio * 100).toFixed(0);

        // Ratio Logic
        if (ratio <= config.financialSafety.safeZoneThreshold) {
          score += config.financialSafety.safeZoneBonus;
          logs.push(`Tỷ lệ Vay/Học phí tốt (${ratioPercent}%): +${config.financialSafety.safeZoneBonus}`);
        } else if (ratio <= config.financialSafety.moderateZoneThreshold) {
          score += config.financialSafety.moderateZoneBonus;
          logs.push(`Tỷ lệ Vay/Học phí TB (${ratioPercent}%): +${config.financialSafety.moderateZoneBonus}`);
        } else if (ratio > config.financialSafety.criticalZoneThreshold) {
          // Gấp đôi học phí -> Phạt nặng
          score += config.financialSafety.criticalZonePenalty;
          logs.push(`⚠️ Vay quá gấp ${config.financialSafety.criticalZoneThreshold} lần học phí (${ratioPercent}%): ${config.financialSafety.criticalZonePenalty}`);
        } else if (ratio > 1) {
          // Lớn hơn học phí -> Phạt nhẹ
          score += config.financialSafety.riskyZonePenalty;
          logs.push(`Vay lớn hơn học phí (${ratioPercent}%): ${config.financialSafety.riskyZonePenalty}`);
        }

        // Absolute Amount Logic (New)
        if (profile.loanAmount > config.financialSafety.absoluteHighValueThreshold) {
          score += config.financialSafety.absoluteHighValuePenalty;
          logs.push(`⚠️ Số tiền vay quá lớn (> ${config.financialSafety.absoluteHighValueThreshold / 1000000}tr): ${config.financialSafety.absoluteHighValuePenalty}`);
        }
      }

      // -- Location Analysis (Real Estate) --
      if (data.locationAnalysis) {
        let locPoints = 0;
        // Region
        if (data.locationAnalysis.region === 'urban') locPoints += config.location.urban;
        else if (data.locationAnalysis.region === 'suburban') locPoints += config.location.suburban;
        else locPoints += config.location.rural;

        // Position
        if (data.locationAnalysis.position === 'main_street') locPoints += config.location.main_street;
        else if (data.locationAnalysis.position === 'alley') locPoints += config.location.alley;
        else locPoints += config.location.deep_alley;

        score += locPoints;
        const regionName = data.locationAnalysis.region === 'urban' ? 'Đô thị' : data.locationAnalysis.region === 'suburban' ? 'Ngoại ô' : 'Nông thôn';
        const posName = data.locationAnalysis.position === 'main_street' ? 'Mặt tiền' : data.locationAnalysis.position === 'alley' ? 'Hẻm xe' : 'Hẻm sâu';

        logs.push(`Bất động sản (${regionName} - ${posName}): ${locPoints > 0 ? '+' : ''}${locPoints}`);
      }

      // -- Other Factors --
      const phonePoints = config.phone[profile.phoneType];
      score += phonePoints;
      logs.push(`Số điện thoại: ${phonePoints > 0 ? '+' : ''}${phonePoints}`);

      let parentPoints = 0;
      if (profile.parentsJob === 'noInfo') parentPoints = config.parents.noInfo;
      else if (profile.parentsJob === 'unstable') parentPoints = config.parents.hasInfo_Unstable;
      else parentPoints = config.parents.hasInfo_Stable;
      score += parentPoints;
      logs.push(`Công việc bố mẹ: ${parentPoints > 0 ? '+' : ''}${parentPoints}`);

      let socialPoints = 0;
      if (profile.socialMedia === 'none') socialPoints = config.social.none;
      else if (profile.socialMedia === 'negative') socialPoints = config.social.has_Negative;
      else socialPoints = config.social.has_Positive;
      score += socialPoints;
      logs.push(`Mạng xã hội: ${socialPoints > 0 ? '+' : ''}${socialPoints}`);

      let pcbPoints = 0;
      if (profile.pcb === 'none') pcbPoints = config.pcb.none;
      else if (profile.pcb === 'bad') pcbPoints = config.pcb.has_Bad;
      else pcbPoints = config.pcb.has_Good;
      score += pcbPoints;
      logs.push(`PCB (Tín dụng): ${pcbPoints > 0 ? '+' : ''}${pcbPoints}`);

      const consistPoints = config.consistency[profile.consistency];
      score += consistPoints;
      logs.push(`Tính hợp lý hồ sơ: ${consistPoints > 0 ? '+' : ''}${consistPoints}`);

      // Final Rounding
      score = Math.round(score * 10) / 10;
      setFinalScore(score);
      setScoreBreakdown(logs);

      // 4. Recommendation Logic
      if (score >= config.passingThreshold) {
        setRecommendation('APPROVE');
      } else if (score < 30 || profile.pcb === 'bad' || profile.consistency === 'unreasonable') {
        setRecommendation('REJECT');
      } else {
        setRecommendation('REVIEW');
      }

    } catch (err) {
      setError("Có lỗi xảy ra khi phân tích. Vui lòng thử lại.");
      console.error(err);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="animate-fade-in pb-20">
      <section className="mb-8">
        <h2 className="text-2xl md:text-3xl font-extrabold text-slate-900 mb-2 flex items-center gap-2">
          <GraduationCap className="text-blue-600" />
          Phân Tích & Thẩm Định Sinh Viên
        </h2>
        <p className="text-slate-500 mb-6 text-sm">
          Đánh giá điểm tín dụng dựa trên trường học, địa chỉ và hồ sơ cá nhân.
        </p>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">

          {/* Input Form */}
          <div className="lg:col-span-1 bg-white p-6 rounded-2xl shadow-sm border border-gray-200 h-fit">
            <form onSubmit={handleAnalyze} className="space-y-5">

              {/* Loan Amount - Updated formatting */}
              <div className="bg-blue-50 p-4 rounded-xl border border-blue-100">
                <label className="block text-sm font-bold text-blue-900 mb-1">Số tiền muốn vay</label>
                <div className="relative">
                  <input
                    type="text"
                    className="block w-full px-4 py-2 bg-white border border-blue-200 rounded-lg focus:ring-2 focus:ring-blue-500 transition-all font-semibold text-gray-900 pr-10"
                    value={displayLoanAmount}
                    onChange={handleLoanAmountChange}
                    placeholder="0"
                  />
                  <span className="absolute right-3 top-2.5 text-gray-400 text-sm font-medium">VNĐ</span>
                </div>
                {/* Money in words */}
                <p className="text-xs text-blue-600 mt-2 text-right font-medium italic">
                  {docSoTien(profile.loanAmount)}
                </p>
              </div>

              {/* University */}
              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-1">Trường Đại học/Cao đẳng <span className="text-red-500">*</span></label>
                <input
                  type="text"
                  required
                  className="block w-full px-4 py-2 bg-gray-50 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 transition-all"
                  placeholder="Nhập tên trường..."
                  value={profile.universityName}
                  onChange={(e) => setProfile({ ...profile, universityName: e.target.value })}
                />
              </div>

              {/* Address - Added Below University */}
              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-1">Địa chỉ thường trú (Hộ khẩu)</label>
                <textarea
                  rows={2}
                  className="block w-full px-4 py-2 bg-gray-50 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 transition-all text-sm"
                  placeholder="VD: 123 Nguyễn Văn Cừ, Phường 4, Quận 5..."
                  value={profile.address}
                  onChange={(e) => setProfile({ ...profile, address: e.target.value })}
                />
                <p className="text-[10px] text-gray-400 mt-1">AI sẽ phân tích giá trị bất động sản tại vị trí này.</p>
              </div>

              {/* Phone Number Quality */}
              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-2">Chất lượng Số điện thoại</label>
                <div className="flex gap-2">
                  {(['bad', 'normal', 'good'] as const).map((type) => (
                    <button
                      key={type}
                      type="button"
                      onClick={() => setProfile({ ...profile, phoneType: type })}
                      className={`flex-1 py-2 text-xs font-medium rounded-lg border transition-all ${profile.phoneType === type
                          ? (type === 'good' ? 'bg-green-100 border-green-500 text-green-700' : type === 'bad' ? 'bg-red-100 border-red-500 text-red-700' : 'bg-blue-100 border-blue-500 text-blue-700')
                          : 'bg-white border-gray-200 text-gray-600 hover:bg-gray-50'
                        }`}
                    >
                      {type === 'bad' ? 'Xấu' : type === 'normal' ? 'Bình thường' : 'Đẹp'}
                    </button>
                  ))}
                </div>
              </div>

              {/* Parents Job */}
              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-2">Công việc Bố mẹ</label>
                <select
                  className="block w-full px-4 py-2 bg-gray-50 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                  value={profile.parentsJob}
                  onChange={(e) => setProfile({ ...profile, parentsJob: e.target.value as any })}
                >
                  <option value="noInfo">Không có thông tin</option>
                  <option value="stable">Có thông tin - Ổn định</option>
                  <option value="unstable">Có thông tin - Không ổn định</option>
                </select>
              </div>

              {/* Social Media */}
              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-2">Mạng xã hội (Facebook/Zalo)</label>
                <div className="flex gap-2">
                  <label className="flex items-center gap-2 text-sm cursor-pointer">
                    <input type="radio" name="social" checked={profile.socialMedia === 'none'} onChange={() => setProfile({ ...profile, socialMedia: 'none' })} />
                    Không có
                  </label>
                  <label className="flex items-center gap-2 text-sm cursor-pointer">
                    <input type="radio" name="social" checked={profile.socialMedia === 'positive'} onChange={() => setProfile({ ...profile, socialMedia: 'positive' })} />
                    Tích cực
                  </label>
                  <label className="flex items-center gap-2 text-sm cursor-pointer">
                    <input type="radio" name="social" checked={profile.socialMedia === 'negative'} onChange={() => setProfile({ ...profile, socialMedia: 'negative' })} />
                    Tiêu cực
                  </label>
                </div>
              </div>

              {/* PCB */}
              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-2">PCB (Lịch sử tín dụng)</label>
                <select
                  className="block w-full px-4 py-2 bg-gray-50 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                  value={profile.pcb}
                  onChange={(e) => setProfile({ ...profile, pcb: e.target.value as any })}
                >
                  <option value="none">Chưa có lịch sử (Trắng)</option>
                  <option value="good">Có - Tốt</option>
                  <option value="bad">Có - Nợ xấu/Chậm trả</option>
                </select>
              </div>

              {/* Consistency */}
              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-2">Tính hợp lý hồ sơ</label>
                <div className="flex gap-2">
                  <button
                    type="button"
                    onClick={() => setProfile({ ...profile, consistency: 'reasonable' })}
                    className={`flex-1 py-2 text-sm font-medium rounded-lg border transition-all ${profile.consistency === 'reasonable'
                        ? 'bg-green-100 border-green-500 text-green-700'
                        : 'bg-white border-gray-200 text-gray-600 hover:bg-gray-50'
                      }`}
                  >
                    Hợp lý
                  </button>
                  <button
                    type="button"
                    onClick={() => setProfile({ ...profile, consistency: 'unreasonable' })}
                    className={`flex-1 py-2 text-sm font-medium rounded-lg border transition-all ${profile.consistency === 'unreasonable'
                        ? 'bg-red-100 border-red-500 text-red-700'
                        : 'bg-white border-gray-200 text-gray-600 hover:bg-gray-50'
                      }`}
                  >
                    Không hợp lý
                  </button>
                </div>
              </div>

              <button
                type="submit"
                disabled={isLoading}
                className="w-full bg-blue-600 hover:bg-blue-700 text-white font-bold py-3 rounded-xl transition-colors disabled:opacity-50 flex items-center justify-center gap-2 mt-4 shadow-lg shadow-blue-200"
              >
                {isLoading ? <Loader2 className="animate-spin" /> : <Calculator size={20} />}
                Phân Tích Hồ Sơ
              </button>
            </form>
          </div>

          {/* Result Section */}
          <div className="lg:col-span-2 space-y-6">

            {error && (
              <div className="bg-red-50 border border-red-200 rounded-xl p-4 flex items-start gap-3 text-red-700">
                <Info className="h-5 w-5 flex-shrink-0 mt-0.5" />
                <p>{error}</p>
              </div>
            )}

            {!uniData && !isLoading && !error && (
              <div className="h-full flex flex-col items-center justify-center text-gray-400 border-2 border-dashed border-gray-200 rounded-2xl p-10 min-h-[300px]">
                <Calculator size={48} className="mb-4 opacity-50" />
                <p>Nhập thông tin bên trái để bắt đầu phân tích</p>
              </div>
            )}

            {uniData && (
              <div className="animate-fade-in-up space-y-6">
                {/* Score Summary Card */}
                {finalScore !== null && recommendation && (
                  <div className={`rounded-2xl p-6 text-white shadow-xl flex flex-col md:flex-row items-center justify-between gap-6 ${recommendation === 'APPROVE' ? 'bg-gradient-to-r from-green-500 to-emerald-700' :
                      recommendation === 'REJECT' ? 'bg-gradient-to-r from-red-500 to-rose-700' :
                        'bg-gradient-to-r from-yellow-500 to-orange-600'
                    }`}>
                    <div className="text-center md:text-left">
                      <p className="text-white/80 font-medium uppercase tracking-wider text-sm mb-1">Kết quả Thẩm định</p>
                      <h3 className="text-4xl font-extrabold flex items-center gap-3 justify-center md:justify-start">
                        {recommendation === 'APPROVE' ? 'ĐỀ XUẤT DUYỆT' :
                          recommendation === 'REJECT' ? 'TỪ CHỐI' : 'CẦN XEM XÉT'}
                        {recommendation === 'APPROVE' ? <CheckCircle2 size={32} /> :
                          recommendation === 'REJECT' ? <XCircle size={32} /> : <AlertTriangle size={32} />}
                      </h3>
                      <p className="mt-2 text-white/90">
                        {recommendation === 'APPROVE' ? 'Hồ sơ đạt đủ điều kiện an toàn.' :
                          recommendation === 'REJECT' ? 'Rủi ro quá cao hoặc vi phạm điều kiện.' : 'Điểm số nằm trong vùng ranh giới.'}
                      </p>
                    </div>
                    <div className="bg-white/20 p-4 rounded-xl backdrop-blur-sm min-w-[150px] text-center">
                      <p className="text-xs uppercase font-bold text-white/80">Tổng Điểm</p>
                      <p className="text-5xl font-black">{finalScore}</p>
                      <p className="text-xs mt-1">/ 100 (ngưỡng duyệt)</p>
                    </div>
                  </div>
                )}

                {/* Real Estate Analysis Block */}
                {uniData.locationAnalysis && (
                  <div className="bg-purple-50 border border-purple-100 rounded-xl p-5 shadow-sm">
                    <h4 className="font-bold text-purple-900 mb-3 flex items-center gap-2">
                      <MapPin size={18} />
                      Thẩm định Bất động sản (AI)
                    </h4>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <div className="bg-white p-3 rounded-lg border border-purple-50">
                        <p className="text-xs text-gray-500 uppercase font-bold mb-1">Phân loại khu vực</p>
                        <div className="flex items-center gap-2">
                          <span className="font-bold text-gray-800">
                            {uniData.locationAnalysis.region === 'urban' ? 'Đô thị / Trung tâm' :
                              uniData.locationAnalysis.region === 'suburban' ? 'Ven đô / Huyện' : 'Nông thôn'}
                          </span>
                          <span className="text-purple-300">|</span>
                          <span className="font-bold text-gray-800">
                            {uniData.locationAnalysis.position === 'main_street' ? 'Mặt tiền / Đường lớn' :
                              uniData.locationAnalysis.position === 'alley' ? 'Hẻm xe hơi' : 'Hẻm sâu / Ngách nhỏ'}
                          </span>
                        </div>
                      </div>
                      <div className="bg-white p-3 rounded-lg border border-purple-50">
                        <p className="text-xs text-gray-500 uppercase font-bold mb-1">Đánh giá giá trị</p>
                        <p className="font-bold text-gray-800">{uniData.locationAnalysis.estimatedValue}</p>
                      </div>
                    </div>
                    <div className="mt-3 text-sm text-purple-800 bg-purple-100/50 p-3 rounded-lg italic">
                      " {uniData.locationAnalysis.riskAssessment} "
                    </div>
                  </div>
                )}

                {/* Breakdown */}
                {scoreBreakdown.length > 0 && (
                  <div className="bg-white border border-gray-200 rounded-xl p-5 shadow-sm">
                    <h4 className="font-bold text-gray-800 mb-3 border-b border-gray-100 pb-2 flex items-center gap-2">
                      <TrendingUp size={18} className="text-blue-600" />
                      Chi tiết điểm số
                    </h4>
                    <ul className="space-y-2 text-sm text-gray-700">
                      {scoreBreakdown.map((log, idx) => (
                        <li key={idx} className="flex justify-between items-center bg-gray-50 px-3 py-2 rounded">
                          <span>{log.split(':')[0]}</span>
                          <span className={`font-bold ${log.includes('+') ? 'text-green-600' : 'text-red-500'}`}>
                            {log.split(':')[1]}
                          </span>
                        </li>
                      ))}
                    </ul>
                  </div>
                )}

                {/* University Info Reuse */}
                <div className="border-t border-gray-200 pt-6">
                  <h4 className="font-bold text-gray-500 uppercase text-xs mb-4">Thông tin trường học (Dữ liệu AI)</h4>
                  <ResultCard data={uniData} />
                </div>
              </div>
            )}
          </div>
        </div>
      </section>
    </div>
  );
};

export default StudentAnalysis;
