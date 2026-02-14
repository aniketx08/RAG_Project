import { motion } from "framer-motion";

export default function About() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-950 via-slate-900 to-indigo-950 text-white relative overflow-hidden">

      {/* Background decorative elements */}
      <div className="fixed inset-0 pointer-events-none">
        <div className="absolute top-16 left-16 w-80 h-80 bg-amber-600/20 rounded-full mix-blend-multiply filter blur-3xl animate-pulse" />
        <div className="absolute bottom-20 right-20 w-80 h-80 bg-indigo-600/20 rounded-full mix-blend-multiply filter blur-3xl animate-pulse" />
      </div>

      <div className="relative pt-24 pb-16 px-6">
        <div className="max-w-4xl mx-auto">
          <motion.div
            initial={{ opacity: 0, y: 40 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
            className="bg-slate-900 border border-slate-800 rounded-2xl shadow-2xl p-12"
          >
            <h1 className="text-4xl font-extrabold mb-8 tracking-tight text-amber-400">
              About Legal AI Assistant
            </h1>

            <div className="space-y-6 text-slate-300 leading-relaxed text-lg">
              <motion.p
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
              >
                Our Legal AI Assistant is revolutionizing how people access legal information. With cutting-edge artificial intelligence and machine learning, we provide instant answers to your legal questions based on verified documents and trusted sources.
              </motion.p>

              <motion.p
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
              >
                Whether you're a business owner, student, or individual seeking legal guidance, our platform offers secure, accurate, and instantaneous legal insights at your fingertips. We combine the power of AI with the rigor of legal standards to ensure every answer is reliable and trustworthy.
              </motion.p>

              <motion.p
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
              >
                Our mission is to democratize access to legal information while maintaining the highest standards of security, accuracy, and compliance. We're committed to helping you navigate complex legal matters with confidence.
              </motion.p>

              {/* Our Values */}
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                className="mt-8 pt-8 border-t border-slate-700"
              >
                <h2 className="text-2xl font-bold text-amber-400 mb-4">Our Values</h2>
                <ul className="space-y-3">
                  <li className="flex items-start gap-3">
                    <span className="text-amber-500 font-bold mt-1">•</span>
                    <span><strong>Accuracy:</strong> Every answer is backed by verified legal documents and sources</span>
                  </li>
                  <li className="flex items-start gap-3">
                    <span className="text-amber-500 font-bold mt-1">•</span>
                    <span><strong>Security:</strong> Your data is protected with enterprise-grade encryption</span>
                  </li>
                  <li className="flex items-start gap-3">
                    <span className="text-amber-500 font-bold mt-1">•</span>
                    <span><strong>Accessibility:</strong> Legal knowledge should be available to everyone</span>
                  </li>
                  <li className="flex items-start gap-3">
                    <span className="text-amber-500 font-bold mt-1">•</span>
                    <span><strong>Innovation:</strong> We continuously improve our AI to serve you better</span>
                  </li>
                </ul>
              </motion.div>

              {/* Why Choose Us */}
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                className="mt-8 pt-8 border-t border-slate-700"
              >
                <h2 className="text-2xl font-bold text-amber-400 mb-4">Why Choose Us?</h2>
                <p>
                  We understand that legal matters are complex and often time-sensitive. Our AI-powered platform eliminates the need to spend hours reading through legal documents or waiting for expensive consultations. Get instant, reliable answers 24/7.
                </p>
              </motion.div>

            </div>

            <motion.p
              initial={{ opacity: 0 }}
              whileInView={{ opacity: 1 }}
              viewport={{ once: true }}
              className="mt-12 pt-8 border-t border-slate-700 text-center text-sm text-slate-400"
            >
              Disclaimer: This is not legal advice. Always consult with a licensed attorney for critical legal matters.
            </motion.p>

          </motion.div>
        </div>
      </div>
    </div>
  );
}
