interface Feature {
  title: string;
  description: string;
  icon: string;
}

const features: Feature[] = [
  {
    title: "Tersedia 24/7",
    description:
      "Dukungan berbasis AI yang bekerja sepanjang waktu, memastikan pelanggan Anda selalu mendapat bantuan saat mereka membutuhkannya.",
    icon: "🌐",
  },
  {
    title: "Sangat Cepat",
    description:
      "Respons instan terhadap pertanyaan pelanggan tanpa waktu tunggu, meningkatkan kepuasan dan retensi.",
    icon: "⚡",
  },
  {
    title: "Integrasi Mudah",
    description:
      "Pengaturan sederhana dengan sistem yang sudah ada. Siap digunakan dengan overhead teknis minimal.",
    icon: "🔌",
  },
  {
    title: "Akurasi Tinggi",
    description:
      "Teknologi NLP canggih memastikan pemahaman yang tepat dan respons yang relevan terhadap pertanyaan kompleks.",
    icon: "🎯",
  },
];

export default function Features() {
  return (
    <section className="py-20 px-4 bg-black text-white">
      <div className="max-w-7xl mx-auto">
        <h2 className="text-4xl md:text-5xl font-bold text-center mb-4">
          Mengapa Memilih Chatbot AI Kami?
        </h2>
        <p className="text-xl text-gray-400 text-center mb-16 max-w-2xl mx-auto">
          Fitur-fitur canggih yang dirancang untuk meningkatkan pengalaman
          layanan pelanggan Anda
        </p>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
          {features.map((feature, index) => (
            <div
              key={index}
              className="bg-white/5 backdrop-blur-sm p-8 rounded-2xl border border-white/10 hover:border-[#00D9FF] transition-all duration-300 hover:shadow-lg hover:shadow-[#00D9FF]/20"
            >
              <div className="text-5xl mb-4">{feature.icon}</div>
              <h3 className="text-2xl font-semibold mb-3">{feature.title}</h3>
              <p className="text-gray-400 leading-relaxed">
                {feature.description}
              </p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
