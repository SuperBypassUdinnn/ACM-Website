import Button from "./Button";

export default function CTA() {
  return (
    <section className="py-20 px-4 bg-black text-white">
      <div className="max-w-4xl mx-auto text-center">
        <h2 className="text-4xl md:text-6xl font-bold mb-6">
          Ready to Transform Your
          <span className="block text-[#00D9FF]">Customer Service?</span>
        </h2>

        <p className="text-xl text-gray-400 mb-10 max-w-2xl mx-auto">
          Join hundreds of businesses already using AI to deliver exceptional
          customer experiences. Try it now — no credit card required.
        </p>

        <Button variant="primary" href="/chat">
          Try Our Chatbot Now
        </Button>
      </div>
    </section>
  );
}
