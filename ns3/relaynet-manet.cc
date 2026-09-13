#include "ns3/aodv-module.h"
#include "ns3/applications-module.h"
#include "ns3/core-module.h"
#include "ns3/dsr-module.h"
#include "ns3/energy-module.h"
#include "ns3/flow-monitor-module.h"
#include "ns3/internet-module.h"
#include "ns3/mobility-module.h"
#include "ns3/network-module.h"
#include "ns3/olsr-module.h"
#include "ns3/wifi-module.h"

#include <algorithm>
#include <array>
#include <cctype>
#include <cmath>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <string>
#include <vector>

using namespace ns3;
using namespace ns3::energy;

namespace
{

constexpr uint32_t FLOW_COUNT = 3;
uint64_t g_transmitted = 0;
uint64_t g_received = 0;
uint64_t g_receivedBytes = 0;
Time g_delaySum = Seconds(0);
Time g_jitterSum = Seconds(0);
double g_firstNodeDeathSeconds = -1.0;
std::array<Time, FLOW_COUNT> g_lastDelay{};
std::array<bool, FLOW_COUNT> g_hasLastDelay{};
std::vector<bool> g_energyDisabled;

void
TraceRemainingEnergy(double oldValue, double newValue)
{
    if (newValue <= 0.0 && g_firstNodeDeathSeconds < 0.0)
    {
        g_firstNodeDeathSeconds = Simulator::Now().GetSeconds();
    }
}

void
HandleRadioDepletion(Ptr<WifiPhy> phy)
{
    phy->SetOffMode();
    if (g_firstNodeDeathSeconds < 0.0)
    {
        g_firstNodeDeathSeconds = Simulator::Now().GetSeconds();
    }
}

void
TraceTransmission(Ptr<const Packet> packet)
{
    ++g_transmitted;
}

void
TraceReception(uint32_t flow,
               Ptr<const Packet> packet,
               const Address& from,
               const Address& localAddress,
               const SeqTsSizeHeader& header)
{
    ++g_received;
    g_receivedBytes += packet->GetSize();

    const Time delay = Simulator::Now() - header.GetTs();
    g_delaySum += delay;
    if (g_hasLastDelay[flow])
    {
        g_jitterSum += delay >= g_lastDelay[flow] ? delay - g_lastDelay[flow]
                                                  : g_lastDelay[flow] - delay;
    }
    g_lastDelay[flow] = delay;
    g_hasLastDelay[flow] = true;
}

std::string
ToUpper(std::string value)
{
    std::transform(value.begin(), value.end(), value.begin(), [](unsigned char ch) {
        return static_cast<char>(std::toupper(ch));
    });
    return value;
}

void
DisableNode(Ptr<Node> node)
{
    Ptr<Ipv4> ipv4 = node->GetObject<Ipv4>();
    if (!ipv4)
    {
        return;
    }

    for (uint32_t interface = 1; interface < ipv4->GetNInterfaces(); ++interface)
    {
        ipv4->SetDown(interface);
    }
}

void
EnforceRelayDepletion(NodeContainer nodes,
                       EnergySourceContainer sources,
                       uint32_t firstRelay,
                       uint32_t relayEnd,
                       double simulationTime)
{
    for (uint32_t index = firstRelay; index < relayEnd; ++index)
    {
        if (!g_energyDisabled[index] && sources.Get(index)->GetRemainingEnergy() <= 0.05)
        {
            DisableNode(nodes.Get(index));
            g_energyDisabled[index] = true;
            if (g_firstNodeDeathSeconds < 0.0)
            {
                g_firstNodeDeathSeconds = Simulator::Now().GetSeconds();
            }
        }
    }

    if (Simulator::Now().GetSeconds() + 1.0 <= simulationTime)
    {
        Simulator::Schedule(Seconds(1.0),
                            &EnforceRelayDepletion,
                            nodes,
                            sources,
                            firstRelay,
                            relayEnd,
                            simulationTime);
    }
}

void
AppendResult(const std::string& outputFile,
             const std::string& protocol,
             const std::string& scenario,
             uint32_t seed,
             uint32_t run,
             uint32_t nodeCount,
             double speed,
             const std::string& offeredRate,
             uint64_t offeredPackets,
             uint64_t sourceTransmitted,
             uint64_t received,
             double pdr,
             double lossRatio,
             double averageDelayMs,
             double averageJitterMs,
             double throughputKbps,
             double energyConsumedJ,
             double networkLifetimeSeconds)
{
    std::ifstream existing(outputFile);
    const bool writeHeader = !existing.good() || existing.peek() == std::ifstream::traits_type::eof();
    existing.close();

    std::ofstream csv(outputFile, std::ios::app);
    if (!csv)
    {
        NS_FATAL_ERROR("Cannot open output file: " << outputFile);
    }

    if (writeHeader)
    {
        csv << "protocol,scenario,seed,run,nodes,max_speed_mps,offered_rate,"
               "offered_packets,source_tx_packets,rx_packets,pdr_percent,loss_ratio_percent,"
               "average_delay_ms,average_jitter_ms,throughput_kbps,energy_consumed_j,"
               "network_lifetime_s\n";
    }

    csv << protocol << ',' << scenario << ',' << seed << ',' << run << ',' << nodeCount << ','
        << std::fixed << std::setprecision(3) << speed << ',' << offeredRate << ',' << offeredPackets
        << ',' << sourceTransmitted << ',' << received << ',' << pdr << ',' << lossRatio << ','
        << averageDelayMs << ',' << averageJitterMs << ',' << throughputKbps << ','
        << energyConsumedJ << ',' << networkLifetimeSeconds << '\n';
}

} // namespace

int
main(int argc, char* argv[])
{
    std::string protocol = "AODV";
    std::string scenario = "normal";
    std::string outputFile = "relaynet-ns3-results.csv";
    uint32_t nodeCount = 20;
    uint32_t seed = 42;
    uint32_t run = 1;
    double simulationTime = 120.0;
    double maxSpeed = 5.0;
    std::string offeredRate = "64kbps";

    CommandLine cmd(__FILE__);
    cmd.AddValue("protocol", "Routing protocol: AODV, OLSR, or DSR", protocol);
    cmd.AddValue("scenario",
                 "Scenario: normal, high_mobility, high_congestion, low_battery, or "
                 "relay_failure",
                 scenario);
    cmd.AddValue("output", "CSV output file", outputFile);
    cmd.AddValue("nodes", "Number of MANET nodes (minimum 8)", nodeCount);
    cmd.AddValue("seed", "Random seed", seed);
    cmd.AddValue("run", "Independent RNG run number", run);
    cmd.AddValue("time", "Simulation duration in seconds", simulationTime);
    cmd.Parse(argc, argv);

    protocol = ToUpper(protocol);
    if (protocol != "AODV" && protocol != "OLSR" && protocol != "DSR")
    {
        NS_FATAL_ERROR("Unsupported protocol: " << protocol << ". Use AODV, OLSR, or DSR.");
    }
    if (nodeCount < 8)
    {
        NS_FATAL_ERROR("At least 8 nodes are required.");
    }

    if (scenario == "high_mobility")
    {
        maxSpeed = 20.0;
    }
    else if (scenario == "high_congestion")
    {
        offeredRate = "256kbps";
    }
    else if (scenario != "normal" && scenario != "low_battery" &&
             scenario != "relay_failure")
    {
        NS_FATAL_ERROR("Unsupported scenario: " << scenario);
    }

    RngSeedManager::SetSeed(seed);
    RngSeedManager::SetRun(run);

    NodeContainer nodes;
    nodes.Create(nodeCount);

    ObjectFactory positionFactory;
    positionFactory.SetTypeId("ns3::RandomRectanglePositionAllocator");
    positionFactory.Set("X", StringValue("ns3::UniformRandomVariable[Min=0.0|Max=500.0]"));
    positionFactory.Set("Y", StringValue("ns3::UniformRandomVariable[Min=0.0|Max=500.0]"));
    Ptr<PositionAllocator> positions = positionFactory.Create()->GetObject<PositionAllocator>();

    MobilityHelper mobility;
    mobility.SetPositionAllocator(positions);
    mobility.SetMobilityModel(
        "ns3::RandomWaypointMobilityModel",
        "Speed",
        StringValue("ns3::UniformRandomVariable[Min=1.0|Max=" + std::to_string(maxSpeed) + "]"),
        "Pause",
        StringValue("ns3::ConstantRandomVariable[Constant=1.0]"),
        "PositionAllocator",
        PointerValue(positions));
    mobility.Install(nodes);

    WifiHelper wifi;
    wifi.SetStandard(WIFI_STANDARD_80211g);

    YansWifiChannelHelper channel = YansWifiChannelHelper::Default();
    channel.AddPropagationLoss("ns3::RangePropagationLossModel", "MaxRange", DoubleValue(250.0));

    YansWifiPhyHelper phy;
    phy.SetChannel(channel.Create());

    WifiMacHelper mac;
    mac.SetType("ns3::AdhocWifiMac");
    NetDeviceContainer devices = wifi.Install(phy, mac, nodes);

    EnergySourceContainer energySources;
    double totalInitialEnergyJ = 0.0;
    for (uint32_t index = 0; index < nodeCount; ++index)
    {
        const bool isRelay = index >= FLOW_COUNT && index < nodeCount - FLOW_COUNT;
        const double initialEnergyJ =
            scenario == "low_battery" && isRelay ? 12.0 : 1000.0;

        BasicEnergySourceHelper sourceHelper;
        sourceHelper.Set("BasicEnergySourceInitialEnergyJ", DoubleValue(initialEnergyJ));
        NodeContainer oneNode(nodes.Get(index));
        EnergySourceContainer oneSource = sourceHelper.Install(oneNode);
        energySources.Add(oneSource);
        totalInitialEnergyJ += initialEnergyJ;

        Ptr<BasicEnergySource> source = DynamicCast<BasicEnergySource>(oneSource.Get(0));
        source->TraceConnectWithoutContext("RemainingEnergy",
                                           MakeCallback(&TraceRemainingEnergy));
    }

    for (uint32_t index = 0; index < nodeCount; ++index)
    {
        Ptr<WifiNetDevice> wifiDevice = DynamicCast<WifiNetDevice>(devices.Get(index));
        WifiRadioEnergyModelHelper radioEnergy;
        radioEnergy.Set("TxCurrentA", DoubleValue(0.280));
        radioEnergy.Set("RxCurrentA", DoubleValue(0.313));
        radioEnergy.SetDepletionCallback(
            MakeBoundCallback(&HandleRadioDepletion, wifiDevice->GetPhy()));
        radioEnergy.Install(devices.Get(index), energySources.Get(index));
    }

    InternetStackHelper internet;
    if (protocol == "AODV")
    {
        AodvHelper routing;
        internet.SetRoutingHelper(routing);
        internet.Install(nodes);
    }
    else if (protocol == "OLSR")
    {
        OlsrHelper routing;
        internet.SetRoutingHelper(routing);
        internet.Install(nodes);
    }
    else
    {
        internet.Install(nodes);
        DsrHelper dsr;
        DsrMainHelper dsrMain;
        dsrMain.Install(dsr, nodes);
    }

    g_energyDisabled.assign(nodeCount, false);
    if (scenario == "low_battery")
    {
        Simulator::Schedule(Seconds(1.0),
                            &EnforceRelayDepletion,
                            nodes,
                            energySources,
                            FLOW_COUNT,
                            nodeCount - FLOW_COUNT,
                            simulationTime);
    }

    Ipv4AddressHelper address;
    address.SetBase("10.1.0.0", "255.255.0.0");
    Ipv4InterfaceContainer interfaces = address.Assign(devices);

    const uint32_t packetSize = 512;
    for (uint32_t flow = 0; flow < FLOW_COUNT; ++flow)
    {
        const uint32_t sourceIndex = flow;
        const uint32_t sinkIndex = nodeCount - 1 - flow;
        const uint16_t port = static_cast<uint16_t>(9000 + flow);

        PacketSinkHelper sink("ns3::UdpSocketFactory",
                              InetSocketAddress(Ipv4Address::GetAny(), port));
        sink.SetAttribute("EnableSeqTsSizeHeader", BooleanValue(true));
        ApplicationContainer sinkApp = sink.Install(nodes.Get(sinkIndex));
        sinkApp.Start(Seconds(0.0));
        sinkApp.Stop(Seconds(simulationTime));
        sinkApp.Get(0)->TraceConnectWithoutContext(
            "RxWithSeqTsSize",
            MakeBoundCallback(&TraceReception, flow));

        OnOffHelper source("ns3::UdpSocketFactory",
                           InetSocketAddress(interfaces.GetAddress(sinkIndex), port));
        source.SetAttribute("PacketSize", UintegerValue(packetSize));
        source.SetAttribute("DataRate", DataRateValue(DataRate(offeredRate)));
        source.SetAttribute("EnableSeqTsSizeHeader", BooleanValue(true));
        source.SetAttribute("OnTime",
                            StringValue("ns3::ConstantRandomVariable[Constant=1.0]"));
        source.SetAttribute("OffTime",
                            StringValue("ns3::ConstantRandomVariable[Constant=0.0]"));

        ApplicationContainer sourceApp = source.Install(nodes.Get(sourceIndex));
        sourceApp.Start(Seconds(10.0 + flow));
        sourceApp.Stop(Seconds(simulationTime - 1.0));
        sourceApp.Get(0)->TraceConnectWithoutContext("Tx", MakeCallback(&TraceTransmission));
    }

    if (scenario == "relay_failure")
    {
        Simulator::Schedule(Seconds(simulationTime / 2.0),
                            &DisableNode,
                            nodes.Get(nodeCount / 2));
    }

    FlowMonitorHelper monitorHelper;
    Ptr<FlowMonitor> monitor = monitorHelper.InstallAll();

    Simulator::Stop(Seconds(simulationTime));
    Simulator::Run();
    monitor->CheckForLostPackets();

    const DataRate configuredRate(offeredRate);
    const double packetInterval =
        packetSize * 8.0 / static_cast<double>(configuredRate.GetBitRate());
    uint64_t offeredPackets = 0;
    for (uint32_t flow = 0; flow < FLOW_COUNT; ++flow)
    {
        const double activeDuration = (simulationTime - 1.0) - (10.0 + flow);
        offeredPackets += static_cast<uint64_t>(std::floor(activeDuration / packetInterval));
    }

    const uint64_t transmitted = offeredPackets;
    const uint64_t sourceTransmitted = g_transmitted;
    const uint64_t received = g_received;
    const uint64_t receivedBytes = g_receivedBytes;
    const uint64_t lost = transmitted >= received ? transmitted - received : 0;
    const double pdr = transmitted == 0 ? 0.0 : 100.0 * received / transmitted;
    const double lossRatio = transmitted == 0 ? 0.0 : 100.0 * lost / transmitted;
    const double averageDelayMs =
        received == 0 ? 0.0 : 1000.0 * g_delaySum.GetSeconds() / received;
    const double averageJitterMs =
        received <= FLOW_COUNT ? 0.0 : 1000.0 * g_jitterSum.GetSeconds() / (received - FLOW_COUNT);
    const double activeTrafficTime = std::max(1.0, simulationTime - 10.0);
    const double throughputKbps = receivedBytes * 8.0 / activeTrafficTime / 1000.0;
    double totalRemainingEnergyJ = 0.0;
    for (uint32_t index = 0; index < energySources.GetN(); ++index)
    {
        totalRemainingEnergyJ += energySources.Get(index)->GetRemainingEnergy();
    }
    const double energyConsumedJ = totalInitialEnergyJ - totalRemainingEnergyJ;
    const double networkLifetimeSeconds =
        g_firstNodeDeathSeconds < 0.0 ? simulationTime : g_firstNodeDeathSeconds;

    AppendResult(outputFile,
                 protocol,
                 scenario,
                 seed,
                 run,
                 nodeCount,
                 maxSpeed,
                 offeredRate,
                 transmitted,
                 sourceTransmitted,
                 received,
                 pdr,
                 lossRatio,
                 averageDelayMs,
                 averageJitterMs,
                 throughputKbps,
                 energyConsumedJ,
                 networkLifetimeSeconds);

    std::cout << "RelayNet NS-3 MANET simulation completed\n"
              << "Protocol: " << protocol << " | Scenario: " << scenario << " | Seed: " << seed
              << " | Run: " << run << '\n'
              << "Offered: " << transmitted << " | Source TX accepted: " << sourceTransmitted
              << " | RX: " << received << " | Lost: " << lost << '\n'
              << std::fixed << std::setprecision(3) << "PDR: " << pdr
              << "% | Loss: " << lossRatio << "% | Delay: " << averageDelayMs
              << " ms | Jitter: " << averageJitterMs << " ms | Throughput: " << throughputKbps
              << " kbps\n"
              << "Energy consumed: " << energyConsumedJ
              << " J | Network lifetime: " << networkLifetimeSeconds << " s\n"
              << "CSV: " << outputFile << '\n';

    Simulator::Destroy();
    return 0;
}
