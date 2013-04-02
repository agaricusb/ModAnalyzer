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

                /*
                blocksBuilder.withElement(Integer.toString(i), anObjectBuilder()
                        .withField("id", num(i))
                        .withField("unlocalizedName", aStringBuilder(block.getUnlocalizedName()))
                        .withField("localizedName", aStringBuilder(block.getLocalizedName()))
                        .withField("hardness", num(block.blockHardness))
                        .withField("material", aStringBuilder();*/

                JsonNode blockNode = object(
                        field("id", number(i)), /** ID of the block. */
                        field("resistence", number(Float.toString(block.blockHardness))), /** Indicates the blocks resistance to explosions. */
                        field("enableStats", booleanNode(block.getEnableStats())),
                        field("needsRandomTick", booleanNode(block.getTickRandomly())),
                        //isBlockContainer
                        //coords
                        field("bounds", string(String.format("%f-%f,%f-%f,%f-%f",
                                block.getBlockBoundsMinX(), block.getBlockBoundsMaxX(),
                                block.getBlockBoundsMinY(), block.getBlockBoundsMaxY(),
                                block.getBlockBoundsMinZ(), block.getBlockBoundsMaxZ())
                                )),
                        field("stepSound", string(""+block.stepSound)),
                        field("particleGravity", number(Float.toString(block.blockParticleGravity))),
                        field("material", string(""+block.blockMaterial)), /** Indicates how many hits it takes to break a block. */
                        field("slipperiness", number(Float.toString(block.slipperiness))),

                        field("unlocalizedName", string(block.getUnlocalizedName())), /** Returns the unlocalized name of this block */
                        //blockIcon?

                        field("isNormalCube", booleanNode(Block.isNormalCube(i))),
                        field("renderAsNormalBlock", booleanNode(block.renderAsNormalBlock())), /** If this block doesn't render as an ordinary block it will return False (examples: signs, buttons, stairs, etc */
                        field("renderType", number(block.getRenderType())), /** The type of render function that is called for this block */

                        field("localizedName", string(block.getLocalizedName())), /** Gets the localized name of this block. Used for the statistics page */
                        field("hardness", number(Float.toString(block.blockHardness))), /** Indicates how many hits it takes to break a block. */

                        field("hasTileEntity", booleanNode(block.hasTileEntity(0))),
                        field("opaqueCube", booleanNode(block.isOpaqueCube())), /** Is this block (a) opaque and (b) a full 1m cube?   */
                        field("canCollideCheck", booleanNode(block.canCollideCheck(0, false))), /** Returns whether this block is collideable based on the arguments passed in  **/
                        field("isCollidable", booleanNode(block.isCollidable())), /** Returns if this block is collidable (only used by Fire). */
                        //field("tickRate", number(block.tickRate(null))))
                        field("quantityDropped", number(block.quantityDropped(random))),
                        field("damageDropped", number(block.damageDropped(0))),
                        //field("explosionResistance", number(Float.toString(block.getExplosionResistance(null))))
                        field("canProvidePower", booleanNode(block.canProvidePower())),
                        //canSilkHarvest
                        field("mobilityFlag", number(block.getMobilityFlag())), /** Returns the mobility information of the block, 0 = free, 1 = can't push but can move over, 2 = total immobility */
                        //getSubBlocks
                        //func_82506_l
                        //field("canDropFromExplosion", boolea(block.canDropFromExplosion(null))),
                        field("hasComparatorInputOverride", booleanNode(block.hasComparatorInputOverride())) /** If this returns true, then comparators facing away from this block will use the value from getComparatorInputOverride instead of the actual redstone signal strength */
                        );
                //blocksBuilder.withElement(
            }
        }

        for (int i = 0; i < Item.itemsList.length; ++i) {
            Item item = Item.itemsList[i];
            if (item != null) {
                System.out.println("Item,"+item.itemID+","+item.getUnlocalizedName()+","+item.getHasSubtypes()+","+item.getPotionEffect()+","+item.getItemEnchantability()+","+item.getItemStackLimit());
            }
        }

        /*
        JsonRootNode json =
        String jsonText = (new PrettyJsonFormatter()).format(json);

        System.out.println("JSON="+jsonText);*/

        Runtime.getRuntime().halt(0);
    }

    // convenience method since argo requires a string
    private JsonNodeBuilder<JsonNode> num(int n) {
        return aNumberBuilder(Integer.toString(n));
    }

    private JsonNodeBuilder<JsonNode> num(float f) {
        return aNumberBuilder(Float.toString(f));
    }
}

