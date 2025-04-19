const fs = require("fs");
async function main() {
  const [deployer] = await ethers.getSigners();
  console.log("Deploying with:", deployer.address);

  const Reg = await ethers.getContractFactory("IdentityRegistry");
  const reg = await Reg.deploy();
  await reg.waitForDeployment();

  const addr = await reg.getAddress();
  console.log("Registry deployed:", addr);

  // write to .env (append or update)
  let env = "";
  if (fs.existsSync(".env")) env = fs.readFileSync(".env", "utf8");
  env = env.replace(/REGISTRY_ADDR=.*/g, "").trim();
  fs.writeFileSync(".env", env + `\nREGISTRY_ADDR=${addr}\n`);
}
main().catch(err => { console.error(err); process.exit(1); });