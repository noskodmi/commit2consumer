import { useAccount, useConnect, useDisconnect } from "wagmi";
import { InjectedConnector } from "wagmi/connectors/injected";
import { useState } from "react";

export default function WalletConnect() {
  const { address, isConnected } = useAccount();
  const { connect, isLoading } = useConnect({
    connector: new InjectedConnector(),
  });
  const { disconnect } = useDisconnect();
  const [error, setError] = useState(null);

  // Format address for display
  const formatAddress = (addr) => {
    if (!addr) return "";
    return `${addr.substring(0, 6)}...${addr.substring(addr.length - 4)}`;
  };

  // Handle connection with error handling
  const handleConnect = async () => {
    try {
      setError(null);
      await connect();
    } catch (err) {
      setError("Failed to connect wallet");
      console.error("Wallet connection error:", err);
    }
  };

  if (isConnected) {
    return (
      <div className="flex items-center space-x-2">
        <span className="bg-blue-700 px-3 py-1 rounded text-sm">
          {formatAddress(address)}
        </span>
        <button
          onClick={() => disconnect()}
          className="bg-red-500 hover:bg-red-600 px-3 py-1 rounded text-sm transition-colors"
        >
          Disconnect
        </button>
      </div>
    );
  }

  return (
    <div>
      <button
        onClick={handleConnect}
        disabled={isLoading}
        className="bg-green-500 hover:bg-green-600 px-4 py-2 rounded font-medium transition-colors disabled:opacity-50"
      >
        {isLoading ? "Connecting..." : "Connect Wallet"}
      </button>
      {error && <p className="text-red-500 text-sm mt-1">{error}</p>}
    </div>
  );
}