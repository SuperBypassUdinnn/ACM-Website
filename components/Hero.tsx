import Button from "./Button";

export default function Hero() {
  return (
    <section className="min-h-screen flex items-center justify-center px-4 py-20 bg-white">
      <div className="max-w-5xl mx-auto text-center">
        <h1 className="text-5xl md:text-7xl font-bold text-black mb-6 leading-tight">
          AI Customer Service
          <span className="block text-[#00D9FF]">That Never Sleeps</span>
        </h1>

        <p className="text-xl md:text-2xl text-gray-600 mb-12 max-w-3xl mx-auto">
          Transform your customer support with intelligent AI chatbots that
          understand, respond, and resolve issues instantly — 24/7.
        </p>

        <div className="flex flex-col sm:flex-row gap-4 justify-center items-center">
          <Button variant="primary">Get Started</Button>
          <Button variant="secondary" href="/chat">
            Try Our Chatbot
          </Button>
        </div>
      </div>
    </section>
  );
}
