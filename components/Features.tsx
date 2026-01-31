interface Feature {
  title: string;
  description: string;
  icon: string;
}

const features: Feature[] = [
  {
    title: "24/7 Availability",
    description:
      "AI-powered support that works around the clock, ensuring your customers always get help when they need it.",
    icon: "🌐",
  },
  {
    title: "Lightning Fast",
    description:
      "Instant responses to customer queries with no wait times, improving satisfaction and retention.",
    icon: "⚡",
  },
  {
    title: "Easy Integration",
    description:
      "Simple setup with your existing systems. Get up and running with minimal technical overhead.",
    icon: "🔌",
  },
  {
    title: "High Accuracy",
    description:
      "Advanced NLP technology ensures precise understanding and relevant responses to complex queries.",
    icon: "🎯",
  },
];

export default function Features() {
  return (
    <section className="py-20 px-4 bg-black text-white">
      <div className="max-w-7xl mx-auto">
        <h2 className="text-4xl md:text-5xl font-bold text-center mb-4">
          Why Choose Our AI Chatbot?
        </h2>
        <p className="text-xl text-gray-400 text-center mb-16 max-w-2xl mx-auto">
          Powerful features designed to elevate your customer service experience
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
