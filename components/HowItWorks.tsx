interface Step {
  number: string;
  title: string;
  description: string;
}

const steps: Step[] = [
  {
    number: "01",
    title: "Integrate",
    description:
      "Connect our API to your platform with just a few lines of code. Works with any tech stack.",
  },
  {
    number: "02",
    title: "Customize",
    description:
      "Train the AI with your business knowledge, FAQs, and product information for accurate responses.",
  },
  {
    number: "03",
    title: "Launch",
    description:
      "Go live instantly and start serving customers with intelligent, automated support.",
  },
];

export default function HowItWorks() {
  return (
    <section className="py-20 px-4 bg-white">
      <div className="max-w-6xl mx-auto">
        <h2 className="text-4xl md:text-5xl font-bold text-center text-black mb-4">
          How It Works
        </h2>
        <p className="text-xl text-gray-600 text-center mb-16 max-w-2xl mx-auto">
          Get started in three simple steps
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
