package agaricus.mods.modanalyzer;

import argo.format.JsonFormatter;
import argo.format.PrettyJsonFormatter;
import argo.jdom.*;
import com.google.common.base.Joiner;
import com.google.common.base.Objects;
import cpw.mods.fml.common.FMLLog;
import cpw.mods.fml.common.Mod;
import cpw.mods.fml.common.Mod.PostInit;
import cpw.mods.fml.common.Mod.PreInit;
import cpw.mods.fml.common.event.FMLInitializationEvent;
import cpw.mods.fml.common.event.FMLPostInitializationEvent;
import cpw.mods.fml.common.event.FMLPreInitializationEvent;
import cpw.mods.fml.common.network.NetworkMod;
import cpw.mods.fml.relauncher.ReflectionHelper;
import net.minecraft.block.Block;
import net.minecraft.item.Item;

import java.util.Random;
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

        Random random = new Random();

        for (int i = 0; i < Block.blocksList.length; ++i) {
            Block block = Block.blocksList[i];
            if (block != null) {
                setObject("block", i);
                put("id", i); //ID of the block.
                put("resistence", block.blockHardness); //Indicates the blocks resistance to explosions.
                put("enableStats", block.getEnableStats());
                put("needsRandomTick", block.getTickRandomly());
                //isBlockContainer
                //coords
                put("bounds", String.format("%f-%f,%f-%f,%f-%f",
                        block.getBlockBoundsMinX(), block.getBlockBoundsMaxX(),
                        block.getBlockBoundsMinY(), block.getBlockBoundsMaxY(),
                        block.getBlockBoundsMinZ(), block.getBlockBoundsMaxZ()));
                put("stepSound", block.stepSound);
                put("particleGravity", block.blockParticleGravity);
                put("material", block.blockMaterial); //Indicates how many hits it takes to break a block.
                put("slipperiness", block.slipperiness);

                put("unlocalizedName", block.getUnlocalizedName()); //Returns the unlocalized name of this block
                        //blockIcon?

                put("isNormalCube", Block.isNormalCube(i));
                put("renderAsNormalBlock", block.renderAsNormalBlock()); //If this block doesn't render as an ordinary block it will return False (examples: signs, buttons, stairs, etc
                put("renderType", block.getRenderType()); //The type of render function that is called for this block

                put("localizedName", block.getLocalizedName()); //Gets the localized name of this block. Used for the statistics page
                put("hardness", block.blockHardness); //Indicates how many hits it takes to break a block.

                put("hasTileEntity", block.hasTileEntity(0));
                put("opaqueCube", block.isOpaqueCube()); //Is this block (a) opaque and (b) a full 1m cube?
                put("canCollideCheck", block.canCollideCheck(0, false)); //Returns whether this block is collideable based on the arguments passed in  *
                put("isCollidable", block.isCollidable()); //Returns if this block is collidable (only used by Fire).
                //put("tickRate", (block.tickRate(null))))
                put("quantityDropped", block.quantityDropped(random));
                put("damageDropped", block.damageDropped(0));
                //put("explosionResistance", (""+block.getExplosionResistance(null)))
                put("canProvidePower", block.canProvidePower());
                //canSilkHarvest
                put("mobilityFlag", block.getMobilityFlag()); //Returns the mobility information of the block, 0 = free, 1 = can't push but can move over, 2 = total immobility
                //getSubBlocks
                //func_82506_l
                //put("canDropFromExplosion", boolea(block.canDropFromExplosion(null)))
                put("hasComparatorInputOverride", block.hasComparatorInputOverride()); //If this returns true, then comparators facing away from this block will use the value from getComparatorInputOverride instead of the actual redstone signal strength
            }
        }

        for (int i = 0; i < Item.itemsList.length; ++i) {
            Item item = Item.itemsList[i];
            if (item != null) {
                System.out.println("Item,"+item.itemID+","+item.getUnlocalizedName()+","+item.getHasSubtypes()+","+item.getPotionEffect()+","+item.getItemEnchantability()+","+item.getItemStackLimit());
            }
        }

        System.out.println("JSON="+stringBuilder.toString());

        Runtime.getRuntime().halt(0);
    }

    private StringBuilder stringBuilder = new StringBuilder();
    private String objectType, objectName;

    private <T> void setObject(String type, T name) {
        this.objectType = type;
        this.objectName = ""+name;
    }
    private <T> void put(String key, T value) {
        stringBuilder.append(objectType + "\t" + objectName + "\t" + key + "\t" + value + "\n");
    }
}

