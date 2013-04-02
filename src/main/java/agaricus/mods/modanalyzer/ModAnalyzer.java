package agaricus.mods.modanalyzer;

import argo.format.JsonFormatter;
import argo.format.PrettyJsonFormatter;
import argo.jdom.*;
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

import static argo.jdom.JsonNodeFactories.*;
import static argo.jdom.JsonNodeBuilders.*;

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

        JsonArrayNodeBuilder blocksBuilder = anArrayBuilder();
        Random random = new Random();

        for (int i = 0; i < Block.blocksList.length; ++i) {
            Block block = Block.blocksList[i];
            if (block != null) {
                blocksBuilder.withElement(anObjectBuilder()
                        .withField("id", aNumberBuilder(""+i)) //ID of the block.
                        .withField("resistence", aNumberBuilder(""+block.blockHardness)) //Indicates the blocks resistance to explosions.
                        .withField("enableStats", aBooleanBuilder(block.getEnableStats()))
                        .withField("needsRandomTick", aBooleanBuilder(block.getTickRandomly()))
                        //isBlockContainer
                        //coords
                        .withField("bounds", aStringBuilder(String.format("%f-%f,%f-%f,%f-%f",
                                block.getBlockBoundsMinX(), block.getBlockBoundsMaxX(),
                                block.getBlockBoundsMinY(), block.getBlockBoundsMaxY(),
                                block.getBlockBoundsMinZ(), block.getBlockBoundsMaxZ())
                                ))
                        .withField("stepSound", aStringBuilder(""+block.stepSound))
                        .withField("particleGravity", aNumberBuilder(""+block.blockParticleGravity))
                        .withField("material", aStringBuilder(""+block.blockMaterial)) //Indicates how many hits it takes to break a block. 
                        .withField("slipperiness", aNumberBuilder(Float.toString(block.slipperiness)))

                        .withField("unlocalizedName", aStringBuilder(block.getUnlocalizedName())) //Returns the unlocalized name of this block 
                        //blockIcon?

                        .withField("isNormalCube", aBooleanBuilder(Block.isNormalCube(i)))
                        .withField("renderAsNormalBlock", aBooleanBuilder(block.renderAsNormalBlock())) //If this block doesn't render as an ordinary block it will return False (examples: signs, buttons, stairs, etc 
                        .withField("renderType", aNumberBuilder(""+block.getRenderType())) //The type of render function that is called for this block 

                        .withField("localizedName", aStringBuilder(block.getLocalizedName())) //Gets the localized name of this block. Used for the statistics page 
                        .withField("hardness", aNumberBuilder(""+block.blockHardness)) //Indicates how many hits it takes to break a block. 

                        .withField("hasTileEntity", aBooleanBuilder(block.hasTileEntity(0)))
                        .withField("opaqueCube", aBooleanBuilder(block.isOpaqueCube())) //Is this block (a) opaque and (b) a full 1m cube?   
                        .withField("canCollideCheck", aBooleanBuilder(block.canCollideCheck(0, false))) //Returns whether this block is collideable based on the arguments passed in  *
                        .withField("isCollidable", aBooleanBuilder(block.isCollidable())) //Returns if this block is collidable (only used by Fire). 
                        //.withField("tickRate", aNumberBuilder(block.tickRate(null))))
                        .withField("quantityDropped", aNumberBuilder(""+block.quantityDropped(random)))
                        .withField("damageDropped", aNumberBuilder(""+block.damageDropped(0)))
                        //.withField("explosionResistance", aNumberBuilder(""+block.getExplosionResistance(null)))
                        .withField("canProvidePower", aBooleanBuilder(block.canProvidePower()))
                        //canSilkHarvest
                        .withField("mobilityFlag", aNumberBuilder(""+block.getMobilityFlag())) //Returns the mobility information of the block, 0 = free, 1 = can't push but can move over, 2 = total immobility 
                        //getSubBlocks
                        //func_82506_l
                        //.withField("canDropFromExplosion", boolea(block.canDropFromExplosion(null)))
                        .withField("hasComparatorInputOverride", aBooleanBuilder(block.hasComparatorInputOverride())) //If this returns true, then comparators facing away from this block will use the value from getComparatorInputOverride instead of the actual redstone signal strength
                    );
            }
        }

        for (int i = 0; i < Item.itemsList.length; ++i) {
            Item item = Item.itemsList[i];
            if (item != null) {
                System.out.println("Item,"+item.itemID+","+item.getUnlocalizedName()+","+item.getHasSubtypes()+","+item.getPotionEffect()+","+item.getItemEnchantability()+","+item.getItemStackLimit());
            }
        }

        JsonRootNode json = blocksBuilder.build();
        String jsonText = (new PrettyJsonFormatter()).format(json);

        System.out.println("JSON="+jsonText);

        Runtime.getRuntime().halt(0);
    }

    private JsonNodeBuilder<JsonNode> aBooleanBuilder(boolean b) {
        return b ? aTrueBuilder() : aFalseBuilder();
    }
}

