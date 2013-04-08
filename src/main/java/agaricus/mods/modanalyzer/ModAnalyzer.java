package agaricus.mods.modanalyzer;

import cpw.mods.fml.common.FMLLog;
import cpw.mods.fml.common.ITickHandler;
import cpw.mods.fml.common.Mod;
import cpw.mods.fml.common.Mod.PostInit;
import cpw.mods.fml.common.Mod.PreInit;
import cpw.mods.fml.common.TickType;
import cpw.mods.fml.common.event.FMLInitializationEvent;
import cpw.mods.fml.common.event.FMLPostInitializationEvent;
import cpw.mods.fml.common.event.FMLPreInitializationEvent;
import cpw.mods.fml.common.network.NetworkMod;
import cpw.mods.fml.common.registry.TickRegistry;
import cpw.mods.fml.relauncher.Side;
import net.minecraft.block.Block;
import net.minecraft.block.material.Material;
import net.minecraft.enchantment.Enchantment;
import net.minecraft.entity.EntityList;
import net.minecraft.item.Item;
import net.minecraft.item.ItemBlock;
import net.minecraft.item.ItemStack;
import net.minecraft.item.crafting.FurnaceRecipes;
import net.minecraft.world.biome.BiomeGenBase;
import net.minecraftforge.oredict.OreDictionary;

import java.io.BufferedWriter;
import java.io.FileWriter;
import java.io.IOException;
import java.util.EnumSet;
import java.util.List;
import java.util.Map;
import java.util.Random;
import java.util.logging.Level;

@Mod(modid = "ModAnalyzer", name = "ModAnalyzer", version = "1.0-SNAPSHOT") // TODO: version from resource
@NetworkMod(clientSideRequired = false, serverSideRequired = false)
public class ModAnalyzer implements ITickHandler {

    private boolean initialized = false;

    @PreInit
    public void preInit(FMLPreInitializationEvent event) {
    }

    @Mod.Init
    public void init(FMLInitializationEvent event) {
    }

    @PostInit
    public void postInit(FMLPostInitializationEvent event) {
        FMLLog.log(Level.FINE, "Loading ModAnalyzer...");

        TickRegistry.registerTickHandler(this, Side.SERVER);
        //TickRegistry.registerTickHandler(this, Side.CLIENT); // TODO
    }

    @Override
    public void tickEnd(EnumSet<TickType> type, Object... tickData) {
        if (initialized) {
            return;
        }
        initialized = true;

        FMLLog.log(Level.FINE, "ModAnalyzer analyzing...");

        dumpBlocks();
        dumpItems();
        dumpBiomes();
        dumpEnchantments();
        dumpEntities();
        dumpSmeltingRecipes();
        dumpOreDict();
        // TODO: crafting recipes

        try {
            BufferedWriter out = new BufferedWriter(new FileWriter("mod-analysis.csv"));
            out.write(stringBuilder.toString());
            out.close();
        } catch (IOException ex) {
            throw new RuntimeException(ex);
        }

        Runtime.getRuntime().halt(0);
    }

    @Override
    public EnumSet<TickType> ticks() {
        return EnumSet.of(TickType.SERVER);
    }

    @Override
    public void tickStart(EnumSet<TickType> type, Object... tickData) {
    }

    @Override
    public String getLabel() {
        return "ModAnalyzer";
    }

    private void dumpBlocks() {
        Random random = new Random(0);

        for (int i = 0; i < Block.blocksList.length; ++i) {
            Block block = Block.blocksList[i];
            if (block != null && !block.getUnlocalizedName().equals("tile.ForgeFiller")) {
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
                put("stepSound", block.stepSound.getStepSound());
                put("particleGravity", block.blockParticleGravity);
                put("material", toString(block.blockMaterial));

                put("isLiquid", block.blockMaterial.isLiquid());
                put("isSolid", block.blockMaterial.isSolid());
                put("canBlockGrass", block.blockMaterial.getCanBlockGrass());
                put("blocksMovement", block.blockMaterial.blocksMovement());
                put("canBurn", block.blockMaterial.getCanBurn());
                put("isReplaceable", block.blockMaterial.isReplaceable());
                put("isOpaque", block.blockMaterial.isOpaque());
                put("isToolNotRequired", block.blockMaterial.isToolNotRequired());
                //func_85157_q

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
    }

    private void dumpItems() {
        for (int i = 0; i < Item.itemsList.length; ++i) {
            Item item = Item.itemsList[i];
            if (item != null) {
                ItemStack itemStack = new ItemStack(item, 1, 0);
                setObject("item", i);
                put("id", i);
                put("itemStackLimit", item.getItemStackLimit());
                put("hasSubtypes", item.getHasSubtypes());
                put("maxDamage", item.getMaxDamage());
                put("isDamageable", item.isDamageable());
                put("localizedName", item.getLocalizedName(itemStack));
                put("unlocalizedName", item.getUnlocalizedName());
                put("hasContainerItem", item.hasContainerItem());
                put("statName", item.getStatName());
                put("isMap", item.isMap());
                put("itemUseAction", item.getItemUseAction(itemStack).name());
                put("maxItemUseDuration", item.getMaxItemUseDuration(itemStack));
                put("potionEffect", item.getPotionEffect());
                put("isPotionIngredient", item.isPotionIngredient());
                put("itemDisplayName", item.getItemDisplayName(itemStack));
                put("isItemTool", item.isItemTool(itemStack));
                put("enchantability", item.getItemEnchantability());
                put("isRepairable", item.isRepairable());
                put("isItemBlock", item instanceof ItemBlock);
            }
        }
    }

    private void dumpBiomes() {
        for (int i = 0; i < BiomeGenBase.biomeList.length; ++i) {
            BiomeGenBase biome = BiomeGenBase.biomeList[i];
            if (biome != null) {
                setObject("biome", i);
                put("id", biome.biomeID);
                put("name", biome.biomeName);
                put("color", biome.color);
                put("topBlock", biome.topBlock); //The block expected to be on the top of this biome
                put("fillerBlock" ,biome.fillerBlock); //The block to fill spots in when not on the top
                //field_76754_C
                put("minHeight", biome.minHeight);
                put("maxHeight", biome.maxHeight);
                put("temperature", biome.temperature);
                put("rainfall", biome.rainfall);
                put("waterColorMultiplier", biome.waterColorMultiplier);
                //put("decorator", biome.theBiomeDecorator);

                put("enableSnow", biome.getEnableSnow());
                put("canSpawnLightningBolt", biome.canSpawnLightningBolt());
                put("isHighHumidity", biome.isHighHumidity());
                put("spawningChance", biome.getSpawningChance());
                put("intRainfall", biome.getIntRainfall());
                put("intTemperature", biome.getIntTemperature());
            }
        }
    }

    private void dumpEnchantments() {
        for (int i = 0; i < Enchantment.enchantmentsList.length; ++i) {
            Enchantment ench = Enchantment.enchantmentsList[i];
            if (ench != null) {
                setObject("enchantment", i);
                put("id", ench.effectId);
                put("weight", ench.getWeight());
                put("minLevel", ench.getMinLevel());
                put("maxLevel", ench.getMaxLevel());
                put("name", ench.getName());
                put("translatedName", ench.getTranslatedName(1));
            }
        }
    }

    private void dumpEntities() {
        for (Object entityIDObject : EntityList.IDtoClassMapping.keySet()) {
            Class entityClass = (Class) EntityList.IDtoClassMapping.get(entityIDObject);
            int entityID = ((Integer) entityIDObject).intValue();
            String name = (String) EntityList.classToStringMapping.get(entityClass);

            setObject("entity", entityID);
            put("name", name);
            put("class", entityClass.getName());
        }
    }

    private void dumpSmeltingRecipes() {
        for (Map.Entry<Integer, ItemStack> entry : ((Map<Integer, ItemStack>) FurnaceRecipes.smelting().getSmeltingList()).entrySet()) {
            int itemID = entry.getKey();
            ItemStack output = entry.getValue();
            setObject("recipes/smelting", itemID);
            put("output", toString(output));
        }
        for (Map.Entry<List<Integer>, ItemStack> entry : FurnaceRecipes.smelting().getMetaSmeltingList().entrySet()) {
            int itemID = entry.getKey().get(0);
            int meta = entry.getKey().get(1);
            ItemStack output = entry.getValue();
            setObject("recipes/smelting", itemID + ":" + meta);
            put("output", toString(output));
        }
    }

    private void dumpOreDict() {
        for (String oreName : OreDictionary.getOreNames()) {
            for (ItemStack oreItem : OreDictionary.getOres(oreName)) {
                // each item -> registered ore name
                setObject("oredict", toString(oreItem));
                put("name", oreName);
            }
        }
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

    private String toString(Material material) {
        if (material == Material.grass) {
            return "grass";
        } else if (material == Material.ground) {
            return "ground";
        } else if (material == Material.wood) {
            return "wood";
        } else if (material == Material.rock) {
            return "rock";
        } else if (material == Material.iron) {
            return "iron";
        } else if (material == Material.anvil) {
            return "anvil";
        } else if (material == Material.water) {
            return "water";
        } else if (material == Material.lava) {
            return "lava";
        } else if (material == Material.leaves) {
            return "leaves";
        } else if (material == Material.plants) {
            return "plants";
        } else if (material == Material.vine) {
            return "vine";
        } else if (material == Material.sponge) {
            return "sponge";
        } else if (material == Material.cloth) {
            return "cloth";
        } else if (material == Material.fire) {
            return "fire";
        } else if (material == Material.sand) {
            return "sand";
        } else if (material == Material.circuits) {
            return "circuits";
        } else if (material == Material.glass) {
            return "glass";
        } else if (material == Material.redstoneLight) {
            return "redstoneLight";
        } else if (material == Material.tnt) {
            return "tnt";
        } else if (material == Material.coral) {
            return "coral";
        } else if (material == Material.ice) {
            return "ice";
        } else if (material == Material.snow) {
            return "snow";
        } else if (material == Material.craftedSnow) {
            return "craftedSnow";
        } else if (material == Material.cactus) {
            return "cactus";
        } else if (material == Material.clay) {
            return "clay";
        } else if (material == Material.pumpkin) {
            return "pumpkin";
        } else if (material == Material.dragonEgg) {
            return "dragonEgg";
        } else if (material == Material.portal) {
            return "portal";
        } else if (material == Material.cake) {
            return "cake";
        } else if (material == Material.web) {
            return "web";
        } else if (material == Material.piston) {
            return "piston";
        } else {
            return material.getClass().getSimpleName();
        }
    }

    private String toString(ItemStack itemStack) {
        if (itemStack == null) {
            return "null";
        }

        StringBuilder sb = new StringBuilder();

        sb.append(itemStack.itemID);
        sb.append(':');

        if (itemStack.getItemDamage() == OreDictionary.WILDCARD_VALUE) {
            sb.append("*");
        } else {
            sb.append(itemStack.getItemDamage());
        }

        // TODO: dump NBT tags, if any present
        // but what format? Norbert? http://www.reddit.com/r/admincraft/comments/1admu5/rfc_norbert_a_new_nbt_format/
        // or something from smbarbour? or custom?

        return sb.toString();
    }
}

