import Button from "./Button";

export default function CTA() {
  return (
    <section className="py-20 px-4 bg-black text-white">
      <div className="max-w-4xl mx-auto text-center">
        <h2 className="text-4xl md:text-6xl font-bold mb-6">
          Siap Mentransformasi
          <span className="block text-[#00D9FF]">Layanan Pelanggan Anda?</span>
        </h2>

        <p className="text-xl text-gray-400 mb-10 max-w-2xl mx-auto">
          Bergabunglah dengan ratusan bisnis yang sudah menggunakan AI untuk
          memberikan pengalaman pelanggan yang luar biasa. Coba sekarang — tanpa
          kartu kredit.
        </p>

        <Button variant="primary" href="/register">
          Mulai Gratis Sekarang
        </Button>
      </div>
    </section>
  );
}
