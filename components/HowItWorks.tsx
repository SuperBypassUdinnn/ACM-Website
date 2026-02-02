interface Step {
  number: string;
  title: string;
  description: string;
}

const steps: Step[] = [
  {
    number: "01",
    title: "Integrasi",
    description:
      "Hubungkan API kami ke platform Anda hanya dengan beberapa baris kode. Bekerja dengan teknologi apa pun.",
  },
  {
    number: "02",
    title: "Kustomisasi",
    description:
      "Latih AI dengan pengetahuan bisnis, FAQ, dan informasi produk Anda untuk respons yang akurat.",
  },
  {
    number: "03",
    title: "Peluncuran",
    description:
      "Langsung online dan mulai melayani pelanggan dengan dukungan otomatis yang cerdas.",
  },
];

export default function HowItWorks() {
  return (
    <section className="py-20 px-4 bg-white">
      <div className="max-w-6xl mx-auto">
        <h2 className="text-4xl md:text-5xl font-bold text-center text-black mb-4">
          Cara Kerjanya
        </h2>
        <p className="text-xl text-gray-600 text-center mb-16 max-w-2xl mx-auto">
          Mulai dalam tiga langkah sederhana
        </p>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-8 md:gap-12">
          {steps.map((step, index) => (
            <div key={index} className="text-center">
              <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-black text-white text-2xl font-bold mb-6">
                {step.number}
              </div>
              <h3 className="text-2xl font-semibold text-black mb-4">
                {step.title}
              </h3>
              <p className="text-gray-600 leading-relaxed">
                {step.description}
              </p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
