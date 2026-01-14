async function main() {
  console.log("Deploying KERIAnchor...");

  const KERIAnchor = await ethers.getContractFactory("KERIAnchor");
  const contract = await KERIAnchor.deploy();

  // Wait for the deployment to finish (ethers v6)
  await contract.waitForDeployment();

  // Get the deployed address
  const address = await contract.getAddress();

  console.log("✅ Contract deployed to:", address);
  console.log("\n📝 Copy this address to your .env file:");
  console.log("CONTRACT_ADDRESS=" + address);
}

main()
  .then(() => process.exit(0))
  .catch((error) => {
    console.error(error);
    process.exit(1);
  });
