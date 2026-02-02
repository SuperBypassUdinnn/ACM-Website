import Button from "./Button";

export default function Hero() {
  return (
    <section className="min-h-screen flex items-center justify-center px-4 py-20 bg-white">
      <div className="max-w-5xl mx-auto text-center">
        <h1 className="text-5xl md:text-7xl font-bold text-black mb-6 leading-tight">
          Layanan Pelanggan AI
          <span className="block text-[#00D9FF]">Yang Tidak Pernah Tidur</span>
        </h1>

        <p className="text-xl md:text-2xl text-gray-600 mb-12 max-w-3xl mx-auto">
          Transformasikan dukungan pelanggan Anda dengan chatbot AI yang
          memahami, merespons, dan menyelesaikan masalah secara instan — 24/7.
        </p>

        <div className="flex flex-col sm:flex-row gap-4 justify-center items-center">
          <Button variant="primary" href="/register">
            Mulai Sekarang
          </Button>
          <Button variant="secondary" href="/chat">
            Coba Demo
          </Button>
        </div>
      </div>
    </section>
  );
}
