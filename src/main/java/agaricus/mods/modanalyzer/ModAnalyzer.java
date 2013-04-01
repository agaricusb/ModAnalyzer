package agaricus.mods.modanalyzer;

import cpw.mods.fml.common.FMLLog;
import cpw.mods.fml.common.Mod;
import cpw.mods.fml.common.Mod.PostInit;
import cpw.mods.fml.common.Mod.PreInit;
import cpw.mods.fml.common.event.FMLInitializationEvent;
import cpw.mods.fml.common.event.FMLPostInitializationEvent;
import cpw.mods.fml.common.event.FMLPreInitializationEvent;
import cpw.mods.fml.common.network.NetworkMod;
import net.minecraft.block.Block;
import net.minecraft.item.Item;

import java.util.logging.Level;

@Mod(modid = "ModAnalyzer", name = "ModAnalyzer", version = "1.0-SNAPSHOT") // TODO: version from resource
@NetworkMod(clientSideRequired = false, serverSideRequired = false)
public class ModAnalyzer {

    @PreInit
    public void preInit(FMLPreInitializationEvent event) {
    }

    @Mod.Init
    public void init(FMLInitializationEvent event) {
    }

    @PostInit
    public void postInit(FMLPostInitializationEvent event) {
        FMLLog.log(Level.FINE, "Loading ModAnalyzer...");

        for (int i = 0; i < Block.blocksList.length; ++i) {
            Block block = Block.blocksList[i];
            if (block != null) {
                System.out.println("Block,"+block.blockID+","+block.getUnlocalizedName()+","+block.getLocalizedName()+","+block.blockHardness+","+block.blockMaterial+","+block.blockParticleGravity+","+block.blockResistance);
            }
        }

        for (int i = 0; i < Item.itemsList.length; ++i) {
            Item item = Item.itemsList[i];
            if (item != null) {
                System.out.println("Item,"+item.itemID+","+item.getUnlocalizedName()+","+item.getHasSubtypes()+","+item.getPotionEffect()+","+item.getItemEnchantability()+","+item.getItemStackLimit());
            }
        }

        Runtime.getRuntime().halt(0);
    }
}

